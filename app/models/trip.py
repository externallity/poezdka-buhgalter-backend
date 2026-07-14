from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    exchange_rate_rub_per_1000_sum: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=Decimal("7"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
