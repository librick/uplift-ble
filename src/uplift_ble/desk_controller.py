import asyncio
import functools
import logging
from collections.abc import Callable
from dataclasses import dataclass

from bleak import BleakClient

from uplift_ble.byte_maps import (
    BYTE_TO_DESK_ERROR_CODE,
    BYTE_TO_DESK_LOCK_STATUS,
    BYTE_TO_DESK_TOUCH_MODE,
    BYTE_TO_DESK_UNIT,
    DESK_CLEAR_HEIGHT_LIMIT_TO_BYTE,
    DESK_TOUCH_MODE_TO_BYTE,
    DESK_UNIT_TO_BYTE,
)
from uplift_ble.desk_enums import (
    DeskClearHeightLimit,
    DeskEventType,
    DeskLockStatus,
    DeskTouchMode,
    DeskUnit,
)
from uplift_ble.packet import (
    PacketNotification,
    create_command_packet,
    parse_notification_packets,
)
from uplift_ble.utils import bytes_to_uint16_be, convert_tenths_mm_to_mm

logger = logging.getLogger(__name__)


@dataclass
class DeskCommand:
    opcode: int
    payload: bytes


def command_writer(skip_wake=False):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Get the command from the decorated function
            command: DeskCommand = func(self, *args, **kwargs)

            # Send wake commands first if needed unless explicitly skipped
            if self.requires_wake and not skip_wake:
                for i in range(3):
                    await self.wake()
                    await asyncio.sleep(0.1)

            # Convert command to packet bytes
            packet = create_command_packet(
                opcode=command.opcode, payload=command.payload
            )

            logger.debug(
                f"{func.__name__}(): sending {len(packet)} bytes: {packet.hex()}"
            )
            await self.client.write_gatt_char(
                self.input_char_uuid, packet, response=False
            )

            # Wait for notifications
            if not skip_wake:
                logger.debug(
                    f"Waiting up to {self._notification_timeout}s for notifications..."
                )
                await asyncio.sleep(self._notification_timeout)
            return packet

        return wrapper

    return decorator


class DeskController:
    """
    BLE-based desk controller for Uplift desks.

    Writes commands and reads responses via BLE characteristics using the
    vendor-specific packet protocol for Uplift desk control.
    """

    def __init__(
        self,
        client: BleakClient,
        input_char_uuid: str,
        output_char_uuid: str,
        requires_wake: bool,
        notification_timeout: float = 1.0,
    ):
        self.client = client
        self.input_char_uuid = input_char_uuid
        self.output_char_uuid = output_char_uuid
        self.requires_wake = requires_wake
        self._notification_timeout = notification_timeout
        self._notification_queue: asyncio.Queue[bytes] = asyncio.Queue()
        self._processor_task = None
        self._listeners = {}
        self._notify_started = False

        # Read-only state, populated by notifications received from the device
        self._height_mm: float | None = None
        self._unit: DeskUnit | None = None
        self._touch_mode: DeskTouchMode | None = None
        self._lock_status: DeskLockStatus | None = None
        self._height_limit_config_max_mm: int | None = None
        self._height_limit_config_min_mm: int | None = None
        self._height_limit_max_mm: int | None = None
        self._height_limit_min_mm: int | None = None
        self._height_preset_1: int | None = None
        self._height_preset_2: int | None = None
        self._height_preset_3: int | None = None
        self._height_preset_4: int | None = None

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    @property
    def height_mm(self) -> float | None:
        """Current desk height in millimeters (read-only)."""
        return self._height_mm

    @property
    def unit(self) -> DeskUnit | None:
        """Display unit preference (read-only)."""
        return self._unit

    @property
    def touch_mode(self) -> DeskTouchMode | None:
        """Button press behavior mode (read-only)."""
        return self._touch_mode

    @property
    def lock_status(self) -> DeskLockStatus | None:
        """Current lock status of the desk (read-only)."""
        return self._lock_status

    @property
    def height_limit_config_max_mm(self) -> int | None:
        """Maximum height limit in millimeters (read-only). From desk's initial configuration values."""
        return self._height_limit_config_max_mm

    @property
    def height_limit_config_min_mm(self) -> int | None:
        """Minimum height limit in millimeters (read-only). From desk's initial configuration values."""
        return self._height_limit_config_min_mm

    @property
    def height_limit_max_mm(self) -> int | None:
        """Maximum height limit in millimeters (read-only)."""
        return self._height_limit_max_mm

    @property
    def height_limit_min_mm(self) -> int | None:
        """Minimum height limit in millimeters (read-only)."""
        return self._height_limit_min_mm

    @property
    def height_preset_1(self) -> int | None:
        """Height preset 1 in unknown units (read-only)."""
        return self._height_preset_1

    @property
    def height_preset_2(self) -> int | None:
        """Height preset 2 in unknown units (read-only)."""
        return self._height_preset_2

    @property
    def height_preset_3(self) -> int | None:
        """Height preset 3 in unknown units (read-only)."""
        return self._height_preset_3

    @property
    def height_preset_4(self) -> int | None:
        """Height preset 4 in unknown units (read-only)."""
        return self._height_preset_4

    async def _notification_handler(self, sender, data: bytes):
        """Callback for BLE notifications"""
        await self._notification_queue.put(data)

    async def start(self):
        """Start processing notifications"""
        if not self._notify_started:
            await self.client.start_notify(
                self.output_char_uuid, self._notification_handler
            )
            self._notify_started = True
        self._processor_task = asyncio.create_task(self._notification_processor())

    async def stop(self):
        """Stop processing notifications"""
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass

        if self._notify_started:
            await self.client.stop_notify(self.output_char_uuid)
            self._notify_started = False

    async def _notification_processor(self):
        while True:
            try:
                data = await self._notification_queue.get()
                if not data:
                    break

                try:
                    packets = parse_notification_packets(data)
                    for packet in packets:
                        self._process_notification_packet(packet)
                except Exception as e:
                    logger.error(f"Error processing packet: {e}")
                    # Continue processing next packets

            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error(f"Fatal error in notification processor: {e}")
                break

    def _process_notification_packet(self, p: PacketNotification):
        """Process a single notification packet"""
        handlers = {
            0x01: self._process_notification_0x01,
            0x02: self._process_notification_0x02,
            0x04: self._process_notification_0x04,
            0x07: self._process_notification_0x07,
            0x0E: self._process_notification_0x0E,
            0x19: self._process_notification_0x19,
            0x1F: self._process_notification_0x1F,
            0x21: self._process_notification_0x21,
            0x22: self._process_notification_0x22,
            0x25: self._process_notification_0x25,
            0x26: self._process_notification_0x26,
            0x27: self._process_notification_0x27,
            0x28: self._process_notification_0x28,
        }

        handler = handlers.get(p.opcode)
        if handler:
            handler(p.payload)
        else:
            logger.debug(f"Unhandled notification opcode 0x{p.opcode:02X}")

    def on(self, event: DeskEventType, handler: Callable):
        """Register an event handler"""
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(handler)

    def _emit(self, event_type: DeskEventType, *args):
        """Emit an event to all registered handlers"""
        for handler in self._listeners.get(event_type, []):
            try:
                handler(*args)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}")

    def _process_notification_0x01(self, payload: bytes) -> None:
        """
        Handle notification with opcode 0x01 (current height).

        The payload contains the current desk height as a 3-byte value:
        - Byte 0: Status/flag byte (anecdotally, always 0x00)
        - Bytes 1-2: Height as 16-bit big-endian integer in tenths of millimeters

        Height values are always in tenths of millimeters regardless of unit settings.
        """
        expected_len = 3
        if len(payload) != expected_len:
            self._log_payload_length_warning(0x01, payload, expected_len)
            return
        # Skip status byte at position 0, extract height from bytes 1-2
        height_tenths_of_mm = bytes_to_uint16_be(payload[1:3])
        self._height_mm = convert_tenths_mm_to_mm(height_tenths_of_mm)
        self._emit(DeskEventType.HEIGHT, self._height_mm)

    def _process_notification_0x02(self, payload: bytes) -> None:
        """
        Handle notification with opcode 0x02 (error).

        The payload contains a 1-byte error code that maps to specific desk error conditions.
        """
        expected_len = 1
        if len(payload) != expected_len:
            self._log_payload_length_warning(0x02, payload, expected_len)
            return
        error_int = payload[0]
        error_code = BYTE_TO_DESK_ERROR_CODE.get(error_int)
        if error_code is None:
            self._log_payload_unknown_enum_warning(0x02, error_int, "error_code")
            return
        self._emit(DeskEventType.ERROR_CODE, error_code)

    def _process_notification_0x04(self, payload: bytes) -> None:
        """
        Handle notification with opcode 0x04 (reset).

        The payload is empty (0 bytes) and indicates the desk is in a state that requires
        someone to physically reset it via a manual reset procedure.
        When the desk is in this state, attached keypads will likely display one of "RST", "ASr", or "RESET".
        """
        expected_len = 0
        if len(payload) != expected_len:
            self._log_payload_length_warning(0x04, payload, expected_len)
            return
        self._emit(DeskEventType.RESET)

    def _process_notification_0x07(self, payload: bytes) -> None:
        """
        Handle notification with opcode 0x07 (height limit configuration).

        The payload contains both height limits as a 4-byte value:
        - Bytes 0-1: Maximum height (16-bit big-endian integer in millimeters)
        - Bytes 2-3: Minimum height (16-bit big-endian integer in millimeters)

        Limit values are always in millimeters, irrespective of the desk's unit settings.

        This notification is typically sent during initial connection setup to provide
        the desk's stored configuration limits. For real-time limit updates during
        operation (e.g., when limits are being adjusted), prefer notifications 0x21 (max)
        and 0x22 (min) which are sent individually as values change.
        """
        expected_len = 4
        if len(payload) != expected_len:
            self._log_payload_length_warning(0x07, payload, expected_len)
            return
        self._height_limit_config_max_mm = bytes_to_uint16_be(payload[0:2])
        self._height_limit_config_min_mm = bytes_to_uint16_be(payload[2:4])
        self._emit(
            DeskEventType.HEIGHT_LIMITS_CONFIGURATION,
            self._height_limit_config_max_mm,
            self._height_limit_config_min_mm,
        )

    def _process_notification_0x0E(self, payload: bytes) -> None:
        """
        Handle notification with opcode 0x0E (display unit preference).

        The payload contains a 1-byte value indicating the unit system for display:
        - 0x00: Centimeters
        - 0x01: Inches

        This setting primarily affects how the desk's attached display (if any) shows heights
        and what unit preference the app should use. The desk firmware always reports
        actual height values in fixed units (tenths of mm for current height, mm for limits)
        regardless of this setting.
        """
        expected_len = 1
        if len(payload) != expected_len:
            self._log_payload_length_warning(0x0E, payload, expected_len)
            return
        unit = BYTE_TO_DESK_UNIT.get(payload[0])
        if unit is None:
            self._log_payload_unknown_enum_warning(0x0E, payload[0], "unit")
            return
        self._unit = unit
        self._emit(DeskEventType.UNIT, self._unit)

    def _process_notification_0x19(self, payload: bytes) -> None:
        """
        Handle notification with opcode 0x19 (touch mode).

        The payload contains a 1-byte value indicating the button press behavior:
        - 0x00: One-touch mode (press once and desk moves to preset automatically)
        - 0x01: Constant-touch mode (must hold button continuously for desk to move)

        In constant-touch mode, releasing the button immediately stops movement for safety.
        """
        expected_len = 1
        if len(payload) != expected_len:
            self._log_payload_length_warning(0x19, payload, expected_len)
            return
        touch_mode = BYTE_TO_DESK_TOUCH_MODE.get(payload[0])
        if touch_mode is None:
            self._log_payload_unknown_enum_warning(0x19, payload[0], "touch_mode")
            return
        self._touch_mode = touch_mode
        self._emit(DeskEventType.TOUCH_MODE, self._touch_mode)

    def _process_notification_0x1F(self, payload: bytes) -> None:
        """
        Handle notification with opcode 0x1F (lock status).

        The payload contains a 1-byte value indicating the desk's lock state:
        - 0x00: Unlocked (all movement controls enabled)
        - 0x01: Locked (movement controls disabled)

        When locked, height adjustment buttons will be unresponsive.
        This prevents accidental adjustments and is useful in environments where the
        desk position should remain fixed.

        On supported desks, the desk can be locked by pressing the "M" key and holding it
        until the display shows "LOC".
        """
        expected_len = 1
        if len(payload) != expected_len:
            self._log_payload_length_warning(0x1F, payload, expected_len)
            return
        lock_status = BYTE_TO_DESK_LOCK_STATUS.get(payload[0])
        if lock_status is None:
            self._log_payload_unknown_enum_warning(0x1F, payload[0], "lock_status")
            return
        self._lock_status = lock_status
        self._emit(DeskEventType.LOCK_STATUS, self._lock_status)

    def _process_notification_0x21(self, payload: bytes) -> None:
        """
        Handle notification with opcode 0x21 (maximum height limit).

        The payload contains the maximum height limit as a 2-byte big-endian integer
        in millimeters, irrespective of the desk's unit settings.

        This notification is sent when the maximum height limit changes, such as during
        limit adjustment mode. Unlike notification 0x07 which sends both height limits together
        during initial setup, this provides real-time updates of just the maximum height limit.
        """
        expected_len = 2
        if len(payload) != expected_len:
            self._log_payload_length_warning(0x21, payload, expected_len)
            return
        self._height_limit_max_mm = bytes_to_uint16_be(payload)
        self._emit(DeskEventType.HEIGHT_LIMIT_MAX, self._height_limit_max_mm)

    def _process_notification_0x22(self, payload: bytes) -> None:
        """
        Handle notification with opcode 0x22 (minimum height limit).

        The payload contains the minimum height limit as a 2-byte big-endian integer
        in millimeters, irrespective of the desk's unit settings.

        This notification is sent when the minimum height limit changes, such as during
        limit adjustment mode. Unlike notification 0x07 which sends both height limits together
        during initial setup, this provides real-time updates of just the minimum height limit.
        """
        expected_len = 2
        if len(payload) != expected_len:
            self._log_payload_length_warning(0x22, payload, expected_len)
            return
        self._height_limit_min_mm = bytes_to_uint16_be(payload)
        self._emit(DeskEventType.HEIGHT_LIMIT_MIN, self._height_limit_min_mm)

    def _process_notification_0x25(self, payload: bytes) -> None:
        """
        Handle notification with opcode 0x25 (height preset 1).

        The payload contains the stored height for preset 1 as a 2-byte big-endian integer.

        WARNING: Units are inconsistent across hardware/firmware versions.
        The raw value is emitted without unit conversion.
        """
        expected_len = 2
        if len(payload) != expected_len:
            self._log_payload_length_warning(0x25, payload, expected_len)
            return
        value = bytes_to_uint16_be(payload)
        self._height_preset_1 = value
        self._emit(DeskEventType.HEIGHT_PRESET_1, self._height_preset_1)

    def _process_notification_0x26(self, payload: bytes) -> None:
        """
        Handle notification with opcode 0x26 (height preset 2).

        The payload contains the stored height for preset 2 as a 2-byte big-endian integer.

        WARNING: Units are inconsistent across hardware/firmware versions.
        The raw value is emitted without unit conversion.
        """
        expected_len = 2
        if len(payload) != expected_len:
            self._log_payload_length_warning(0x26, payload, expected_len)
            return
        value = bytes_to_uint16_be(payload)
        self._height_preset_2 = value
        self._emit(DeskEventType.HEIGHT_PRESET_2, self._height_preset_2)

    def _process_notification_0x27(self, payload: bytes) -> None:
        """
        Handle notification with opcode 0x27 (height preset 3).

        The payload contains the stored height for preset 3 as a 2-byte big-endian integer.

        WARNING: Units are inconsistent across hardware/firmware versions.
        The raw value is emitted without unit conversion.
        """
        expected_len = 2
        if len(payload) != expected_len:
            self._log_payload_length_warning(0x27, payload, expected_len)
            return
        value = bytes_to_uint16_be(payload)
        self._height_preset_3 = value
        self._emit(DeskEventType.HEIGHT_PRESET_3, self._height_preset_3)

    def _process_notification_0x28(self, payload: bytes) -> None:
        """
        Handle notification with opcode 0x28 (height preset 4).

        The payload contains the stored height for preset 4 as a 2-byte big-endian integer.

        WARNING: Units are inconsistent across hardware/firmware versions.
        The raw value is emitted without unit conversion.
        """
        expected_len = 2
        if len(payload) != expected_len:
            self._log_payload_length_warning(0x28, payload, expected_len)
            return
        value = bytes_to_uint16_be(payload)
        self._height_preset_4 = value
        self._emit(DeskEventType.HEIGHT_PRESET_4, self._height_preset_4)

    def _log_payload_length_warning(
        self, opcode: int, payload: bytes, expected_len: int
    ) -> None:
        logger.warning(
            f"Invalid payload length for notification 0x{opcode:02X}: "
            f"expected_len={expected_len}, actual_len={len(payload)}, payload_hex={payload.hex()}"
        )

    def _log_payload_unknown_enum_warning(
        self, opcode: int, payload_value: int, enum_name: str
    ) -> None:
        logger.warning(
            f"Unknown {enum_name} value in notification 0x{opcode:02X}: "
            f"value=0x{payload_value:02X}"
        )

    @command_writer(skip_wake=True)
    def wake(self) -> DeskCommand:
        return DeskCommand(opcode=0x00, payload=b"")

    @command_writer()
    def move_up(self) -> DeskCommand:
        return DeskCommand(opcode=0x01, payload=b"")

    @command_writer()
    def move_down(self) -> DeskCommand:
        return DeskCommand(opcode=0x02, payload=b"")

    @command_writer()
    def move_to_height_preset_1(self) -> DeskCommand:
        return DeskCommand(opcode=0x05, payload=b"")

    @command_writer()
    def move_to_height_preset_2(self) -> DeskCommand:
        return DeskCommand(opcode=0x06, payload=b"")

    @command_writer()
    def request_height_limits(self) -> DeskCommand:
        return DeskCommand(opcode=0x07, payload=b"")

    @command_writer()
    def set_calibration_offset(self, calibration_offset: int) -> DeskCommand:
        if not 0 <= calibration_offset <= 0xFFFF:
            raise ValueError("calibration_offset not in range [0,65535]")
        payload = calibration_offset.to_bytes(2, "big")
        return DeskCommand(opcode=0x10, payload=payload)

    @command_writer()
    def set_height_limit_max(self, max_height: int) -> DeskCommand:
        if not 0 <= max_height <= 0xFFFF:
            raise ValueError("max_height not in range [0,65535]")
        payload = max_height.to_bytes(2, "big")
        return DeskCommand(opcode=0x11, payload=payload)

    @command_writer()
    def set_touch_mode(self, touch_mode: DeskTouchMode) -> DeskCommand:
        try:
            touch_mode_byte = DESK_TOUCH_MODE_TO_BYTE[touch_mode]
        except KeyError:
            raise ValueError(f"Unsupported touch_mode: {touch_mode}")
        return DeskCommand(opcode=0x19, payload=bytes([touch_mode_byte]))

    @command_writer()
    def move_to_specified_height(self, height: int) -> DeskCommand:
        if not isinstance(height, int) or not 0 <= height <= 0xFFFF:
            raise ValueError("height must be an integer in range [0,65535]")
        payload = height.to_bytes(2, "big")
        return DeskCommand(opcode=0x1B, payload=payload)

    @command_writer()
    def set_current_height_as_height_limit_max(self) -> DeskCommand:
        return DeskCommand(opcode=0x21, payload=b"")

    @command_writer()
    def set_current_height_as_height_limit_min(self) -> DeskCommand:
        return DeskCommand(opcode=0x22, payload=b"")

    @command_writer()
    def clear_height_limit(self, limit: DeskClearHeightLimit) -> DeskCommand:
        try:
            limit_byte = DESK_CLEAR_HEIGHT_LIMIT_TO_BYTE[limit]
        except KeyError:
            raise ValueError(f"Unsupported limit: {limit}")
        return DeskCommand(opcode=0x23, payload=bytes([limit_byte]))

    @command_writer()
    def stop_movement(self) -> DeskCommand:
        return DeskCommand(opcode=0x2B, payload=b"")

    @command_writer()
    def set_units(self, unit: DeskUnit) -> DeskCommand:
        try:
            unit_byte = DESK_UNIT_TO_BYTE[unit]
        except KeyError:
            raise ValueError(f"Unsupported unit: {unit}")
        return DeskCommand(opcode=0x0E, payload=bytes([unit_byte]))

    @command_writer()
    def reset(self) -> DeskCommand:
        return DeskCommand(opcode=0xFE, payload=b"")
