def compute_split(amount: int, ordered_user_ids: list[int]) -> list[tuple[int, int]]:
    """Делит amount поровну между ordered_user_ids (уже отсортированы по display_order —
    вызывающая сторона отвечает за порядок). Остаток от целочисленного деления достаётся
    по одному первым участникам в этом порядке — идентично текущему handleSplit() в Code.gs.
    """
    count = len(ordered_user_ids)
    base = amount // count
    remainder = amount % count
    return [
        (uid, base + (1 if idx < remainder else 0))
        for idx, uid in enumerate(ordered_user_ids)
    ]
