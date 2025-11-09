from enum import Enum


class DeskEventType(Enum):
    """Enumeration of desk notification events."""

    HEIGHT = "height"
    ERROR_CODE = "error_code"
    RESET = "reset"
    HEIGHT_LIMITS_CONFIGURATION = "height_limits_configuration"
    UNIT = "unit"
    TOUCH_MODE = "touch_mode"
    LOCK_STATUS = "lock_status"
    HEIGHT_LIMIT_MAX = "height_limit_max"
    HEIGHT_LIMIT_MIN = "height_limit_min"
    HEIGHT_PRESET_1 = "height_preset_1"
    HEIGHT_PRESET_2 = "height_preset_2"
    HEIGHT_PRESET_3 = "height_preset_3"
    HEIGHT_PRESET_4 = "height_preset_4"


class DeskErrorCode(Enum):
    """
    Error codes reported by the desk controller.
    """

    E01 = "E01"
    E02 = "E02"
    E03 = "E03"
    E04 = "E04"
    E05 = "E05"
    E06 = "E06"
    E07 = "E07"
    E08 = "E08"
    E09 = "E09"
    E10 = "E10"
    E11 = "E11"
    E12 = "E12"
    E13 = "E13"
    H01 = "H01"
    H02 = "H02"
    LOCK = "LOCK"


class DeskClearHeightLimit(Enum):
    """Clear height limit settings supported by the desk controller."""

    MAX = "max"
    MIN = "min"


class DeskUnit(Enum):
    """Unit settings supported by the desk controller."""

    CENTIMETERS = "centimeters"
    INCHES = "inches"


class DeskTouchMode(Enum):
    """
    Touch modes supported by the desk controller.
    """

    ONE_TOUCH = "one_touch"
    CONSTANT_TOUCH = "constant_touch"


class DeskLockStatus(Enum):
    """
    Lock states supported by the desk controller.
    """

    UNLOCKED = "unlocked"
    LOCKED = "locked"
