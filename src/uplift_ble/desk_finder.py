import logging

from uplift_ble.desk_scanner import DeskScanner, DeskScannerProtocol
from uplift_ble.desk_validator import DeskValidator, DeskValidatorProtocol
from uplift_ble.models import DiscoveredDesk

logger = logging.getLogger(__name__)


class DeskFinder:
    """
    Finds and validates BLE desk devices.

    This is a convenience class that combines scanning for BLE devices and
    validating them as supported desks. It orchestrates DeskScanner and
    DeskValidator to provide a simple one-step discovery process.

    Warning:
        Home Assistant integrations should not use this class. Instead, use
        DeskValidator directly with Home Assistant's bluetooth.async_discovered_service_info()
        API for device discovery.
    """

    def __init__(
        self,
        desk_scanner: DeskScannerProtocol | None = None,
        desk_validator: DeskValidatorProtocol | None = None,
    ):
        self._desk_scanner = desk_scanner or DeskScanner()
        self._desk_validator = desk_validator or DeskValidator()

    async def find(
        self,
        timeout_scanner: float = 10.0,
        timeout_validator: float = 10.0,
    ) -> list[DiscoveredDesk]:
        """
        Scan for and validate BLE desks.

        Args:
            timeout_scanner: Time in seconds to scan for devices.
            timeout_validator: Time in seconds per device for validation.

        Returns:
            A list of valid desks.
        """
        logger.debug(f"Scanning for nearby desks, timeout: {timeout_scanner}")
        devices = await self._desk_scanner.scan(timeout=timeout_scanner)
        logger.debug(f"Scanning finished, found {len(devices)} device(s)")

        if len(devices) == 0:
            logger.debug("No devices found")
            return []

        logger.debug(
            f"Found {len(devices)} desk-like devices, performing validation..."
        )
        desks = await self._desk_validator.validate_devices(
            devices=devices, timeout=timeout_validator
        )
        logger.debug(f"Validation finished, found {len(desks)} desk(s)")

        if len(desks) == 0:
            logger.debug("No desks found")
            return []

        return desks
