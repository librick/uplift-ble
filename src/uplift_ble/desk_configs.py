"""BLE configuration definitions for different desk variants."""

from dataclasses import dataclass
from enum import Enum

from bleak.uuids import normalize_uuid_16


class DeskVariant(Enum):
    """Supported desk variants identified by their service UUID prefix."""

    JIECANG_0x00FF = "jiecang_0x00ff"
    JIECANG_0xFF00 = "jiecang_0xff00"
    JIECANG_0xFE60 = "jiecang_0xfe60"
    JIECANG_0xFF12 = "jiecang_0xff12"
    OMNIDESK_0xFE60 = "omnidesk_0xfe60"
    OMNIDESK_0xFF12 = "omnidesk_0xff12"


@dataclass
class DeskConfig:
    """
    Configuration for a specific desk type.

    This dataclass defines the BLE service and characteristic UUIDs required
    to communicate with a particular desk model. Each desk type has its own
    unique set of UUIDs that identify the service and characteristics used
    for control commands, status updates, and device naming.
    """

    desk_variant: DeskVariant  # The variant/hardware revision of the desk. Inferred from advertised services and characteristics.
    service_uuid: str  # The primary service used to disambiguate this type of desk. Likely vendor-specific.
    input_char_uuid: str  # A characteristic used for sending commands to the desk. Likely vendor-specific.
    output_char_uuid: str  # A characteristic used to retrieve notifications from the desk. Likely vendor-specific.
    name_char_uuid: str  # A characteristic used to access the device name of the desk.
    requires_wake: bool = True  # Whether wake commands should be sent.
    command_sync_bytes: bytes = b"\xf1\xf1"  # Sync bytes for command packets. Default is 0xF1F1 for Uplift. Omnidesk uses 0xF2F2.
    notification_sync_bytes: bytes = b"\xf2\xf2"  # Sync bytes for notification packets. Default is 0xF2F2 for Uplift. Omnidesk uses 0xF1F1.
    height_scale_factor: float = 0.1  # Scale factor for height values. Uplift: 0.1 (tenths of mm), Omnidesk: 1.0 (mm directly).


# Mapping of BLE services to desk properties
DESK_CONFIGS_BY_SERVICE: dict[str, DeskConfig] = {
    "000000ff-0000-1000-8000-00805f9b34fb": DeskConfig(
        desk_variant=DeskVariant.JIECANG_0x00FF,
        service_uuid=normalize_uuid_16(0x00FF),
        input_char_uuid=normalize_uuid_16(0x01FF),
        output_char_uuid=normalize_uuid_16(0x02FF),
        name_char_uuid=normalize_uuid_16(0x36EF),
    ),
    "0000fe60-0000-1000-8000-00805f9b34fb": DeskConfig(
        desk_variant=DeskVariant.OMNIDESK_0xFE60,
        service_uuid=normalize_uuid_16(0xFE60),
        input_char_uuid=normalize_uuid_16(0xFE61),
        output_char_uuid=normalize_uuid_16(0xFE62),
        name_char_uuid=normalize_uuid_16(0xFE63),
        command_sync_bytes=b"\xf2\xf2",  # Omnidesk uses 0xF2F2 for commands instead of 0xF1F1
        notification_sync_bytes=b"\xf1\xf1",  # Omnidesk uses 0xF1F1 for notifications instead of 0xF2F2
        height_scale_factor=1.0,  # Omnidesk height is in mm (tenths of cm), not tenths of mm
    ),
    "0000ff00-0000-1000-8000-00805f9b34fb": DeskConfig(
        desk_variant=DeskVariant.JIECANG_0xFF00,
        service_uuid=normalize_uuid_16(0xFF00),
        input_char_uuid=normalize_uuid_16(0xFF01),
        output_char_uuid=normalize_uuid_16(0xFF02),
        name_char_uuid=normalize_uuid_16(0xFE63),
    ),
    "0000ff12-0000-1000-8000-00805f9b34fb": DeskConfig(
        desk_variant=DeskVariant.OMNIDESK_0xFF12,
        service_uuid=normalize_uuid_16(0xFF12),
        input_char_uuid=normalize_uuid_16(0xFF01),
        output_char_uuid=normalize_uuid_16(0xFF02),
        name_char_uuid=normalize_uuid_16(0xFF06),
        command_sync_bytes=b"\xf2\xf2",  # Omnidesk uses 0xF2F2 for commands instead of 0xF1F1
        notification_sync_bytes=b"\xf1\xf1",  # Omnidesk uses 0xF1F1 for notifications instead of 0xF2F2
        height_scale_factor=1.0,  # Omnidesk height is in mm (tenths of cm), not tenths of mm
    ),
}

# Sanity check that the keys of the dictionary match the service_uuid fields.
assert all(
    key == config.service_uuid for key, config in DESK_CONFIGS_BY_SERVICE.items()
), "Service UUID keys must match config service_uuid values"

DESK_SERVICE_UUIDS = list(DESK_CONFIGS_BY_SERVICE.keys())
