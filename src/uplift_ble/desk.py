#!/usr/bin/env python3
"""
Module: uplift_ble.desk
Handles connecting to an Uplift BLE desk, sending commands, and logging notifications.
"""
import asyncio
from contextlib import suppress
import functools
import logging
from typing import Callable, Dict, Optional
from bleak import BleakClient

from uplift_ble.ble_characteristics import (
    BLE_CHAR_UUID_DIS_FIRMWARE_REV,
    BLE_CHAR_UUID_DIS_HARDWARE_REV,
    BLE_CHAR_UUID_DIS_MANUFACTURER_NAME,
    BLE_CHAR_UUID_DIS_MODEL_NUMBER,
    BLE_CHAR_UUID_DIS_PNP_ID,
    BLE_CHAR_UUID_DIS_SERIAL_NUMBER,
    BLE_CHAR_UUID_DIS_SOFTWARE_REV,
    BLE_CHAR_UUID_DIS_SYSTEM_ID,
    BLE_CHAR_UUID_UPLIFT_DESK_CONTROL,
    BLE_CHAR_UUID_UPLIFT_DESK_OUTPUT,
)
from uplift_ble.ble_services import BLE_SERVICE_UUID_DEVICE_INFORMATION_SERVICE
from uplift_ble.packet import (
    PacketNotification,
    create_command_packet,
    parse_notification_packets,
)
from uplift_ble.units import (
    convert_hundredths_mm_to_whole_mm,
    convert_mm_to_in,
)

logger = logging.getLogger(__name__)


def command_writer(func):
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        # Ensure BLE client is connected.
        if not self._connected:
            await self.connect()

        # If we need to send a wake command first, do so here, avoiding recursive case.
        is_wake_func = func.__name__ == "wake"
        if self.requires_wake and not is_wake_func:
            # Send a flurry of wake commands in rapid succession.
            for i in range(3):
                await self.wake()
                await asyncio.sleep(0.1)

        # Build and send packet.
        packet: bytes = func(self, *args, **kwargs)
        logger.info(f"{func.__name__}(): sending {len(packet)} bytes: {packet.hex()}")
        await self._client.write_gatt_char(self.char_uuid_control, packet)

        # Allow time for any notifications to arrive.
        if not is_wake_func:
            logger.info(
                f"Waiting up to {self._notification_timeout}s for notifications..."
            )
            await asyncio.sleep(self._notification_timeout)
        return packet

    return wrapper


class Desk:
    """
    BLE controller for standing desk.

    Attributes:
        on_notification_height: Called when a height notification is received.
            Receives height in millimeters.
        on_notification_rst: Called when an RST/error notification is received.
            The desk likely requires a manual reset when this fires.
        on_notification_calibration_height: Called when a calibration height notification is received.
            Receives calibration height in millimeters.
        on_notification_height_limit_max: Called when a height limit max notification is received.
            Receives height limit max in millimeters.
    """

    def __init__(
        self,
        address: str,
        requires_wake: bool = False,
        char_uuid_control: str = BLE_CHAR_UUID_UPLIFT_DESK_CONTROL,
        char_uuid_output: str = BLE_CHAR_UUID_UPLIFT_DESK_OUTPUT,
        notification_timeout: float = 5.0,
    ):
        self.address = address
        self.requires_wake = requires_wake
        self.char_uuid_control = char_uuid_control
        self.char_uuid_output = char_uuid_output
        self._client = BleakClient(address)
        self._connected = False
        self._notification_timeout = notification_timeout
        self._last_known_height_mm: int | None = None

        # Callbacks
        self.on_notification_height: Optional[Callable[[int], None]] = None
        self.on_notification_rst: Optional[Callable[[], None]] = None
        self.on_notification_calibration_height: Optional[Callable[[int], None]] = None
        self.on_notification_height_limit_max: Optional[Callable[[int], None]] = None

    async def connect(self):
        if not self._connected:
            logger.info(f"Connecting to {self.address}…")
            await self._client.connect()
            self._connected = True
            logger.info("Connected.")
            logger.info(f"Subscribing to notifications on {self.char_uuid_output}.")
            await self._client.start_notify(
                self.char_uuid_output, self._notification_handler
            )
            logger.info("Subscribed.")

    async def disconnect(self):
        if self._connected:
            logger.info("Disconnecting…")
            # BlueZ adapters have been known to throw an EOFError exception when the bus closes.
            with suppress(EOFError):
                await self._client.disconnect()
            self._connected = False
            logger.info("Disconnected.")

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.disconnect()

    def _notification_handler(self, sender: int, data: bytearray):
        """
        Handler for incoming notifications. Logs raw data, updates state, and parses packets.
        """
        logger.debug(f"Received notification from {sender}: {data.hex()}")
        packets = parse_notification_packets(data)
        logger.info(f"Received {len(packets)} notification packet(s).")
        for p in packets:
            self._process_notification_packet(p)

    async def get_device_information(self) -> Dict[str, Optional[str]]:
        """
        Read standard BLE Device Information Service chars and return them by name.
        """
        if not self._connected:
            await self.connect()

        char_uuids: Dict[str, str] = {
            "manufacturer_name": BLE_CHAR_UUID_DIS_MANUFACTURER_NAME,
            "model_number": BLE_CHAR_UUID_DIS_MODEL_NUMBER,
            "serial_number": BLE_CHAR_UUID_DIS_SERIAL_NUMBER,
            "hardware_revision": BLE_CHAR_UUID_DIS_HARDWARE_REV,
            "firmware_revision": BLE_CHAR_UUID_DIS_FIRMWARE_REV,
            "software_revision": BLE_CHAR_UUID_DIS_SOFTWARE_REV,
            "system_id": BLE_CHAR_UUID_DIS_SYSTEM_ID,
            "pnp_id": BLE_CHAR_UUID_DIS_PNP_ID,
        }

        info: Dict[str, Optional[str]] = {}

        try:
            self._client.services.get_service(
                BLE_SERVICE_UUID_DEVICE_INFORMATION_SERVICE
            )
        except Exception:
            return info

        for name, uuid in char_uuids.items():
            try:
                raw = await self._client.read_gatt_char(uuid)
                if not raw:
                    info[name] = None
                elif name in ("system_id", "pnp_id"):
                    info[name] = raw.hex()
                else:
                    info[name] = raw.decode("utf-8", errors="ignore").rstrip("\x00")
            except Exception:
                info[name] = None

        return info

    @command_writer
    def wake(self) -> bytes:
        return create_command_packet(opcode=0x00, payload=b"")

    @command_writer
    def move_up(self) -> bytes:
        return create_command_packet(opcode=0x01, payload=b"")

    @command_writer
    def move_down(self) -> bytes:
        return create_command_packet(opcode=0x02, payload=b"")

    @command_writer
    def move_to_height_preset_1(self) -> bytes:
        return create_command_packet(opcode=0x05, payload=b"")

    @command_writer
    def move_to_height_preset_2(self) -> bytes:
        return create_command_packet(opcode=0x06, payload=b"")

    @command_writer
    def request_height_limits(self) -> bytes:
        return create_command_packet(opcode=0x07, payload=b"")

    @command_writer
    def set_calibration_offset(self, calibration_offset: int) -> bytes:
        if not 0 <= calibration_offset <= 0xFFFF:
            raise ValueError("calibration_offset not in range [0,65535]")
        payload = calibration_offset.to_bytes(2, "big")
        return create_command_packet(opcode=0x10, payload=payload)

    @command_writer
    def set_height_limit_max(self, max_height: int) -> bytes:
        if not 0 <= max_height <= 0xFFFF:
            raise ValueError("max_height not in range [0,65535]")
        payload = max_height.to_bytes(2, "big")
        return create_command_packet(opcode=0x11, payload=payload)

    @command_writer
    def move_to_specified_height(self, height: int) -> bytes:
        if not isinstance(height, int) or not 0 <= height <= 0xFFFF:
            raise ValueError("height must be an integer in range [0,65535]")
        payload = height.to_bytes(2, "big")
        return create_command_packet(opcode=0x1B, payload=payload)

    @command_writer
    def set_current_height_as_height_limit_max(self) -> bytes:
        return create_command_packet(opcode=0x21, payload=b"")

    @command_writer
    def set_current_height_as_height_limit_min(self) -> bytes:
        return create_command_packet(opcode=0x22, payload=b"")

    @command_writer
    def clear_height_limit_max(self) -> bytes:
        return create_command_packet(opcode=0x23, payload=bytes([0x01]))

    @command_writer
    def clear_height_limit_min(self) -> bytes:
        return create_command_packet(opcode=0x23, payload=bytes([0x02]))

    @command_writer
    def stop_movement(self) -> bytes:
        return create_command_packet(opcode=0x2B, payload=b"")

    @command_writer
    def set_units_to_centimeters(self) -> bytes:
        return create_command_packet(opcode=0x0E, payload=bytes([0x00]))

    @command_writer
    def set_units_to_inches(self) -> bytes:
        return create_command_packet(opcode=0x0E, payload=bytes([0x01]))

    @command_writer
    def reset(self) -> bytes:
        return create_command_packet(opcode=0xFE, payload=b"")

    async def get_current_height(self) -> int | None:
        """
        Requests a height update and returns the last observed desk height in mm.
        """
        await self.request_height_limits()
        return self._last_known_height_mm

    def _process_notification_packet(self, p: PacketNotification):
        if p.opcode == 0x01:
            hundredths_of_mm = int.from_bytes(p.payload, byteorder="big", signed=False)
            mm = convert_hundredths_mm_to_whole_mm(hundredths_of_mm)
            inches = convert_mm_to_in(mm)
            logger.info(
                f"- Received packet, opcode=0x{p.opcode:02X}, current height: {mm} mm (~{inches} in)"
            )
            # Important! Update the class state with this most-recently reported height.
            self._last_known_height_mm = mm
            # Invoke callback.
            if self.on_notification_height is not None:
                self.on_notification_height(mm)
        elif p.opcode == 0x04:
            logger.info(
                f"- Received packet, opcode=0x{p.opcode:02X}, desk is reporting an error state (RST) and likely needs to be manually reset"
            )
            # Invoke callback.
            if self.on_notification_rst is not None:
                self.on_notification_rst()
        elif p.opcode == 0x10:
            mm = int.from_bytes(p.payload, byteorder="big", signed=False)
            inches = convert_mm_to_in(mm)
            logger.info(
                f"- Received packet, opcode=0x{p.opcode:02X}, calibration height: {mm} mm (~{inches} in)"
            )
            # Invoke callback.
            if self.on_notification_calibration_height is not None:
                self.on_notification_calibration_height(mm)
        elif p.opcode == 0x11:
            mm = int.from_bytes(p.payload, byteorder="big", signed=False)
            inches = convert_mm_to_in(mm)
            logger.info(
                f"- Received packet, opcode=0x{p.opcode:02X}, height limit max: {mm} mm (~{inches} in)"
            )
            # Invoke callback.
            if self.on_notification_height_limit_max is not None:
                self.on_notification_height_limit_max(mm)
        elif p.opcode == 0x12:
            # Avoid running the command with the 0x12 opcode!
            # The 0x12 command takes a 2-byte payload, but setting it to various values causes strange and potentially dangerous behavior.
            # For example, some payloads make the desk movement jerky, other payloads make the desk move quickly.
            # If you do change this value, anecdotally, a payload of [0x01, 0x00] restores normal behavior.
            # It also appears to affect the scaling used for the height display.
            # Until its behavior is better understood, we recommend avoiding it!
            raw = p.payload.hex()
            logger.info(
                f"- Received packet, opcode=0x{p.opcode:02X}, internal configuration value. Support for this packet type is partial and experimental, payload: 0x{raw}"
            )
        elif p.opcode == 0x25:
            raw = p.payload.hex()
            logger.info(
                f"- Received packet, opcode=0x{p.opcode:02X}, height preset 1. Support for this packet type is partial and experimental, payload: 0x{raw}"
            )
        elif p.opcode == 0x26:
            raw = p.payload.hex()
            logger.info(
                f"- Received packet, opcode=0x{p.opcode:02X}, height preset 2. Support for this packet type is partial and experimental, payload: 0x{raw}"
            )
        elif p.opcode == 0x27:
            raw = p.payload.hex()
            logger.info(
                f"- Received packet, opcode=0x{p.opcode:02X}, height preset 3. Support for this packet type is partial and experimental, payload: 0x{raw}"
            )
        elif p.opcode == 0x28:
            raw = p.payload.hex()
            logger.info(
                f"- Received packet, opcode=0x{p.opcode:02X}, height preset 4. Support for this packet type is partial and experimental, payload: 0x{raw}"
            )
        else:
            logger.info(
                f"- Received packet, opcode=0x{p.opcode:02X}, unknown opcode. Please make a PR if you know what this is."
            )
