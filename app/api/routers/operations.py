import uuid
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.api.deps import get_auth, get_current_user, require_admin
from app.config import settings
from app.database import get_db
from app.models.operation import ExpenseCategory, Operation, OperationSource, OperationType
from app.models.trip import Trip
from app.models.user import User
from app.schemas.balance import BalanceOut
from app.schemas.operation import (
    OperationCreateIn,
    OperationCreateResult,
    OperationOut,
    SplitCreateIn,
    SplitCreateResult,
    SplitShareOut,
)
from app.services.balance import compute_balance, rub_to_sum
from app.services.split import compute_split
from app.services.telegram_notify import notify_if_negative

router = APIRouter(prefix="/api/v1/operations", tags=["operations"])


@router.post("", response_model=OperationCreateResult)
def create_operation(
    body: OperationCreateIn,
    auth: tuple[User, str] = Depends(get_auth),
    db: Session = Depends(get_db),
):
    current_user, source = auth

    target_user_id = current_user.id
    if body.user_id is not None and body.user_id != current_user.id:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Only admin can act on behalf of another user")
        target_user_id = body.user_id

    target_user = db.get(User, target_user_id)
    if not target_user or target_user.trip_id != settings.ACTIVE_TRIP_ID:
        raise HTTPException(status_code=404, detail="Target user not found")

    amount = body.amount
    if body.currency.upper() == "RUB":
        trip = db.get(Trip, settings.ACTIVE_TRIP_ID)
        rate = float(trip.exchange_rate_rub_per_1000_sum)
        amount = rub_to_sum(amount, rate)

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    category = body.category
    if body.type == OperationType.TOPUP:
        category = None
    elif category is None:
        category = ExpenseCategory.OTHER

    operation = Operation(
        trip_id=settings.ACTIVE_TRIP_ID,
        user_id=target_user_id,
        created_by_user_id=current_user.id,
        type=body.type,
        amount=amount,
        category=category,
        comment=body.comment,
        source=OperationSource(source),
    )
    db.add(operation)
    db.commit()
    db.refresh(operation)

    balance = compute_balance(db, settings.ACTIVE_TRIP_ID, target_user_id)
    notify_if_negative(target_user.telegram_id, balance["balance_sum"])

    return OperationCreateResult(
        operation=OperationOut.model_validate(operation),
        balance=BalanceOut(user_id=target_user_id, name=target_user.name, **balance),
    )


@router.post("/split", response_model=SplitCreateResult)
def create_split(
    body: SplitCreateIn,
    auth: tuple[User, str] = Depends(get_auth),
    db: Session = Depends(get_db),
):
    current_user, source = auth
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")

    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    if not body.participant_user_ids:
        raise HTTPException(status_code=400, detail="participant_user_ids required")

    participants = (
        db.query(User)
        .filter(User.id.in_(body.participant_user_ids), User.trip_id == settings.ACTIVE_TRIP_ID)
        .order_by(User.display_order)
        .all()
    )
    if len(participants) != len(set(body.participant_user_ids)):
        raise HTTPException(status_code=404, detail="Some participant_user_ids not found")

    ordered_ids = [u.id for u in participants]
    shares = compute_split(body.amount, ordered_ids)
    users_by_id = {u.id: u for u in participants}

    split_group_id = uuid.uuid4()
    operations: list[Operation] = []
    for user_id, share in shares:
        op = Operation(
            trip_id=settings.ACTIVE_TRIP_ID,
            user_id=user_id,
            created_by_user_id=current_user.id,
            type=OperationType.EXPENSE,
            amount=share,
            category=body.category or ExpenseCategory.OTHER,
            comment=body.comment or "Общий расход",
            source=OperationSource(source),
            split_group_id=split_group_id,
        )
        db.add(op)
        operations.append(op)
    db.commit()
    for op in operations:
        db.refresh(op)

    breakdown = []
    for user_id, share in shares:
        u = users_by_id[user_id]
        breakdown.append(SplitShareOut(user_id=user_id, name=u.name, amount=share))
        balance = compute_balance(db, settings.ACTIVE_TRIP_ID, user_id)
        notify_if_negative(u.telegram_id, balance["balance_sum"])

    return SplitCreateResult(
        operations=[OperationOut.model_validate(op) for op in operations],
        breakdown=breakdown,
    )


@router.get("", response_model=list[OperationOut])
def list_operations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    user_id: int | None = Query(None),
    category: ExpenseCategory | None = Query(None),
    type: OperationType | None = Query(None),
    date_from: date | None = Query(None, alias="from"),
    date_to: date | None = Query(None, alias="to"),
    q: str | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
):
    query = db.query(Operation).filter(
        Operation.trip_id == settings.ACTIVE_TRIP_ID,
        Operation.deleted_at.is_(None),
    )

    if not current_user.is_admin:
        query = query.filter(Operation.user_id == current_user.id)
    elif user_id is not None:
        query = query.filter(Operation.user_id == user_id)

    if category is not None:
        query = query.filter(Operation.category == category)
    if type is not None:
        query = query.filter(Operation.type == type)
    if date_from is not None:
        query = query.filter(Operation.created_at >= datetime.combine(date_from, datetime.min.time()))
    if date_to is not None:
        query = query.filter(Operation.created_at <= datetime.combine(date_to, datetime.max.time()))
    if q:
        query = query.filter(Operation.comment.ilike(f"%{q}%"))

    ops = query.order_by(Operation.created_at.desc()).offset(offset).limit(limit).all()
    return [OperationOut.model_validate(op) for op in ops]
