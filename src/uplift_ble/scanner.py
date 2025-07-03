from bleak import BleakScanner

from uplift_ble.ble_services import BLE_SERVICE_UUID_UPLIFT_DISCOVERY


class DeskScanner:
    @staticmethod
    async def discover(timeout: float = 5.0) -> list[str]:
        """
        Returns a list of BLE addresses for any discovered desks.
        """
        # Currently this scanner only discovers Uplift desks by service UUID.
        # To support other desk makes/models, refactor to accept a list of service UUIDs or
        # subclass/configure different desk scanners.
        target_services = [BLE_SERVICE_UUID_UPLIFT_DISCOVERY]
        devices = await BleakScanner.discover(
            timeout=timeout, service_uuids=target_services
        )

        return [d.address for d in devices]
