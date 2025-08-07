from decimal import ROUND_HALF_UP, Decimal


def convert_mm_to_in(mm: int | float) -> float:
    """
    Converts a value in millimeters to an approximate value in inches, rounding using half-up to one decimal place.
    """
    # The conversion factor used is intentionally inexact to match the hardware behavior.
    return round_half_up(mm * 0.039, num_digits=1)


def convert_hundredths_mm_to_whole_mm(hundredths_of_mm: int) -> int:
    """
    Converts a value in hundredths of a millimeter to millimeters, rounding using half-up to the nearest whole number.
    """
    # 1 hundredth of a millimeter = 0.01 mm
    return round_half_up(hundredths_of_mm * 0.01)


def convert_in_to_mm(inches: int | float) -> float:
    """
    Converts a value in inches to millimeters.
    """
    # 1 inch = 25.4 mm
    return inches * 25.4


def convert_cm_to_mm(cm: int | float) -> float:
    """
    Converts a value in centimeters to a value in millimeters.
    """
    return cm * 10


def round_half_up(value: int | float, num_digits=0):
    """
    By default, the Python 3 built-in round() function uses "banker's rounding",
    or "round-half-to-even" rather than rounding up, for example, 0.5.
    We use round-half-up to better approximate the Uplift hardware.
    """
    quant = Decimal("1e{}".format(-num_digits))
    return float(Decimal(value).quantize(quant, rounding=ROUND_HALF_UP))
