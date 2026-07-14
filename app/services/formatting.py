def format_amount(n: int | float) -> str:
    """Формат "1 461 000" — как fmt() в текущем боте (Code.gs)."""
    sign = "-" if n < 0 else ""
    n = abs(round(n))
    return sign + f"{n:,}".replace(",", " ")
