import logging
from collections.abc import Sequence
from typing import Protocol

from bleak import BleakScanner, BLEDevice

from uplift_ble.ble_protos import BLEDeviceProtocol
from uplift_ble.desk_configs import DESK_SERVICE_UUIDS

logger = logging.getLogger(__name__)


class DeskScannerProtocol(Protocol):
    async def scan(self, timeout: float = 5.0) -> list[BLEDeviceProtocol]: ...


class DeskScanner:
    """
    Scans for BLE devices advertising desk service UUIDs.

    This scanner discovers nearby Bluetooth Low Energy devices that advertise
    specific service UUIDs associated with desk devices. It wraps Bleak's
    discovery mechanism and filters for relevant devices.

    Warning:
        Home Assistant integrations should not use this class directly.
        Use DeskValidator with Home Assistant's Bluetooth APIs instead,
        as Home Assistant manages Bluetooth scanning centrally.
    """

    def __init__(self, service_uuids: Sequence[str] | None = None):
        """
        Initialize the desk scanner.

        Args:
            service_uuids: Optional sequence of service UUIDs to filter for.
                If not provided, uses the default desk service UUIDs.
        """
        self._service_uuids = list(service_uuids or DESK_SERVICE_UUIDS)

    async def scan(self, timeout: float = 10.0) -> list[BLEDevice]:
        """
        Scan for BLE devices advertising the configured service UUIDs.

        Args:
            timeout: Time in seconds to scan for devices.

        Returns:
            List of discovered BLE devices matching the service UUIDs.
        """
        logger.debug(
            f"Starting BLE device discovery across {len(self._service_uuids)} service UUID(s)"
        )
        return await BleakScanner.discover(
            timeout=timeout,
            service_uuids=self._service_uuids,
        )
