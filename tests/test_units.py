import pytest
from uplift_ble.units import (
    convert_mm_to_inches,
    convert_hundredths_of_mm_to_mm,
    round_half_up,
)


@pytest.mark.parametrize(
    "input,expected",
    [
        (0, 0),
        (254, 9.9),
        (508, 19.8),
        (762, 29.7),
    ],
)
def test_convert_mm_to_inches(input: float, expected: float):
    actual = convert_mm_to_inches(input)
    assert actual == expected


@pytest.mark.parametrize(
    "input,expected",
    [(0, 0), (100, 1), (1000, 10), (10000, 100), (40, 0), (50, 1), (60, 1)],
)
def test_convert_hundredths_of_mm_to_mm(input: float, expected: float):
    actual = convert_hundredths_of_mm_to_mm(input)
    assert actual == expected


@pytest.mark.parametrize(
    "input,num_digits,expected",
    [
        (0, 0, 0),
        (0.4, 0, 0),
        (0.5, 0, 1),
        (0.6, 0, 1),
        (1.1, 0, 1),
        (1.4, 0, 1),
        (1.5, 0, 2),
        (1.6, 0, 2),
        (0, 1, 0),
        (0.4, 1, 0.4),
        (0.5, 1, 0.5),
        (0.6, 1, 0.6),
        (1.1, 1, 1.1),
        (1.4, 1, 1.4),
        (1.5, 1, 1.5),
        (1.6, 1, 1.6),
    ],
)
def test_round_half_up(input: float, num_digits: int, expected: float):
    actual = round_half_up(input, num_digits=num_digits)
    assert actual == expected
