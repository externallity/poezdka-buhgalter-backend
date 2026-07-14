import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl

from fastapi import HTTPException


def verify_telegram_init_data(init_data: str, bot_token: str, max_age_seconds: int) -> dict:
    """Проверяет подпись Telegram WebApp initData.

    Схема из официальной документации Telegram (не общая, а именно эта формула):
    secret_key = HMAC_SHA256(key="WebAppData", msg=bot_token)
    computed_hash = HMAC_SHA256(key=secret_key, msg=data_check_string)
    """
    try:
        pairs = dict(parse_qsl(init_data, strict_parsing=True))
    except ValueError:
        raise HTTPException(status_code=401, detail="Malformed initData")

    received_hash = pairs.pop("hash", None)
    if not received_hash:
        raise HTTPException(status_code=401, detail="initData missing hash")

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        raise HTTPException(status_code=401, detail="Invalid initData signature")

    auth_date = int(pairs.get("auth_date", 0))
    if time.time() - auth_date > max_age_seconds:
        raise HTTPException(status_code=401, detail="initData expired")

    if "user" in pairs:
        pairs["user"] = json.loads(pairs["user"])

    return pairs
