import httpx

from app.config import settings
from app.services.formatting import format_amount

TOPUP_INSTRUCTIONS = (
    "\U0001F4B3 Как пополнить баланс:\n"
    "Сбербанк > Перевод зарубеж > Выбрать Узбекистан > "
    "Ввести номер карты 8600490434413571 AMIR MAKHMUDOV > Ввести сумму > Подтвердить"
)


def send_telegram_message(chat_id: int, text: str) -> None:
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        httpx.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
    except httpx.HTTPError:
        pass  # не роняем запрос из-за сбоя уведомления


def notify_if_negative(telegram_id: int | None, balance_sum: int) -> None:
    if balance_sum >= 0 or not telegram_id:
        return
    text = (
        f"⚠️ Внимание: твой баланс ушёл в минус на {format_amount(abs(balance_sum))} сум. "
        f"Пожалуйста, пополни на эту сумму.\n\n{TOPUP_INSTRUCTIONS}"
    )
    send_telegram_message(telegram_id, text)
