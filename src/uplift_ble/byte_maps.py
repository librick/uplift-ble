from typing import TypeVar

from uplift_ble.desk_enums import (
    DeskClearHeightLimit,
    DeskErrorCode,
    DeskLockStatus,
    DeskTouchMode,
    DeskUnit,
)

BYTE_TO_DESK_ERROR_CODE: dict[int, DeskErrorCode] = {
    0x01: DeskErrorCode.E01,
    0x02: DeskErrorCode.E02,
    0x03: DeskErrorCode.E03,
    0x04: DeskErrorCode.E04,
    0x05: DeskErrorCode.E05,
    0x06: DeskErrorCode.E06,
    0x07: DeskErrorCode.E07,
    0x08: DeskErrorCode.E08,
    0x09: DeskErrorCode.E09,
    0x0A: DeskErrorCode.E10,
    0x0B: DeskErrorCode.E11,
    0x0C: DeskErrorCode.E12,
    0x0D: DeskErrorCode.E13,
    0x0E: DeskErrorCode.H01,
    0x0F: DeskErrorCode.H02,
    0x10: DeskErrorCode.LOCK,
}

BYTE_TO_DESK_CLEAR_HEIGHT_LIMIT: dict[int, DeskClearHeightLimit] = {
    0x01: DeskClearHeightLimit.MAX,
    0x02: DeskClearHeightLimit.MIN,
}


BYTE_TO_DESK_UNIT: dict[int, DeskUnit] = {
    0x00: DeskUnit.CENTIMETERS,
    0x01: DeskUnit.INCHES,
}

BYTE_TO_DESK_TOUCH_MODE: dict[int, DeskTouchMode] = {
    0x00: DeskTouchMode.ONE_TOUCH,
    0x01: DeskTouchMode.CONSTANT_TOUCH,
}

BYTE_TO_DESK_LOCK_STATUS: dict[int, DeskLockStatus] = {
    0x00: DeskLockStatus.UNLOCKED,
    0x01: DeskLockStatus.LOCKED,
}


T = TypeVar("T")


def _reverse_mapping(d: dict[int, T]) -> dict[T, int]:
    return {v: k for k, v in d.items()}


DESK_CLEAR_HEIGHT_LIMIT_TO_BYTE = _reverse_mapping(BYTE_TO_DESK_CLEAR_HEIGHT_LIMIT)
DESK_UNIT_TO_BYTE = _reverse_mapping(BYTE_TO_DESK_UNIT)
DESK_TOUCH_MODE_TO_BYTE = _reverse_mapping(BYTE_TO_DESK_TOUCH_MODE)
