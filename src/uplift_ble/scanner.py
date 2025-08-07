import asyncio
from dataclasses import dataclass
from typing import Optional

from bleak import BleakScanner

from uplift_ble.ble_services import (
    BLE_SERVICE_UUID_UPLIFT_DISCOVERY_LIERDA_V1,
    BLE_SERVICE_UUID_UPLIFT_DISCOVERY_LIERDA_V2,
)


@dataclass
class DiscoveredDesk:
    """
    Represents a device found during device discovery that appears to be an Uplift desk.
    """

    address: str
    """BLE MAC address of the device (e.g., 'F1:45:F1:XX:XX:XX')."""
    advertised_service_uuids: list[str]
    """List of service UUIDs advertised in BLE advertisement packets."""
    name: Optional[str] = None
    """Human-readable device name from BLE advertisement, if available."""


class DeskScanner:
    @staticmethod
    async def discover(timeout: float = 5.0) -> list[DiscoveredDesk]:
        """
        Returns a list of discovered devices that look like standing desks.
        """
        target_services = [
            BLE_SERVICE_UUID_UPLIFT_DISCOVERY_LIERDA_V1,
            BLE_SERVICE_UUID_UPLIFT_DISCOVERY_LIERDA_V2,
        ]

        # Use BleakScanner with a detection callback to access advertisement data.
        discovered = {}

        def detection_callback(device, advertisement_data):
            if device.address not in discovered:
                all_advertised_service_uuids = advertisement_data.service_uuids or []

                discovered[device.address] = DiscoveredDesk(
                    address=device.address,
                    advertised_service_uuids=all_advertised_service_uuids,
                    name=device.name,
                )

        scanner = BleakScanner(
            detection_callback=detection_callback, service_uuids=target_services
        )

        await scanner.start()
        await asyncio.sleep(timeout)
        await scanner.stop()

        return list(discovered.values())
