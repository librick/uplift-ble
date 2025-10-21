from decimal import ROUND_HALF_UP, Decimal


def bytes_to_uint16_be(data: bytes) -> int:
    if len(data) != 2:
        raise ValueError(f"Expected 2 bytes, got {len(data)}")
    return int.from_bytes(data, byteorder="big")


def convert_tenths_mm_to_mm(tenths_mm: int) -> float:
    return tenths_mm / 10.0


def convert_cm_to_mm(cm: int | float) -> float:
    """
    Converts a value in centimeters to a value in millimeters.
    """
    return cm * 10


def convert_in_to_mm(inches: int | float) -> float:
    """
    Converts a value in inches to millimeters.
    """
    # 1 inch = 25.4 mm
    return inches * 25.4


def round_half_up(value: int | float, num_digits=0) -> float:
    """
    By default, the Python 3 built-in round() function uses "banker's rounding",
    or "round-half-to-even" rather than rounding up, for example, 0.5.
    We use round-half-up to better approximate the Uplift hardware.
    """
    quant = Decimal(f"1e{-num_digits}")
    return float(Decimal(value).quantize(quant, rounding=ROUND_HALF_UP))
