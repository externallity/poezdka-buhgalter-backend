from app.services.split import compute_split


def test_even_split():
    result = compute_split(600000, [10, 20, 30, 40])
    assert result == [(10, 150000), (20, 150000), (30, 150000), (40, 150000)]


def test_remainder_goes_to_first_in_order():
    # 800003 / 8 участников = 100000 каждому + остаток 3, который уходит
    # первым трём в порядке следования ordered_user_ids (аналог PARTICIPANTS).
    ids = [1, 2, 3, 4, 5, 6, 7, 8]
    result = compute_split(800003, ids)
    amounts = [amount for _, amount in result]
    assert amounts == [100001, 100001, 100001, 100000, 100000, 100000, 100000, 100000]
    assert sum(amounts) == 800003


def test_single_participant_gets_everything():
    result = compute_split(50000, [7])
    assert result == [(7, 50000)]


def test_order_matters_for_remainder_not_input_order():
    # Тот же набор ids, но переданный в другом порядке — вызывающая сторона
    # (роутер) обязана сортировать по display_order ДО вызова compute_split.
    result = compute_split(10, [3, 1, 2])
    assert result == [(3, 4), (1, 3), (2, 3)]
