from app.services.balance import rub_to_sum, sum_to_rub


def test_sum_to_rub_matches_known_rate():
    # 1000 сум = 7 рублей (курс из текущего бота)
    assert sum_to_rub(1000, 7) == 7
    # 671429 * 7 / 1000 = 4700.003, округляется до 2 знаков -> 4700.0
    assert sum_to_rub(671429, 7) == 4700.0


def test_rub_to_sum_matches_known_rate():
    # 4700 рублей -> сум, как в существующей истории операций Искана
    assert rub_to_sum(4700, 7) == 671429  # round(4700 * 1000 / 7)


def test_round_trip_close_enough():
    original_rub = 3000
    sum_amount = rub_to_sum(original_rub, 7)
    back_to_rub = sum_to_rub(sum_amount, 7)
    assert abs(back_to_rub - original_rub) < 1
