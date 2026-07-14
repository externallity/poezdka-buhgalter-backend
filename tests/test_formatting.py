from app.services.formatting import format_amount


def test_format_thousands():
    assert format_amount(1461000) == "1 461 000"


def test_format_negative():
    assert format_amount(-428571) == "-428 571"


def test_format_small():
    assert format_amount(500) == "500"


def test_format_zero():
    assert format_amount(0) == "0"
