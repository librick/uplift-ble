import logging
from collections.abc import Callable, Sequence
from typing import Protocol

from bleak import BleakClient

from uplift_ble.ble_helpers import gatt_characteristics_to_uuids
from uplift_ble.ble_protos import (
    BLEClientProtocol,
    BLEDeviceProtocol,
    GATTServiceProtocol,
)
from uplift_ble.desk_configs import DESK_CONFIGS_BY_SERVICE, DeskConfig
from uplift_ble.models import DiscoveredDesk

logger = logging.getLogger(__name__)


ClientFactory = Callable[..., BLEClientProtocol]


class DeskValidatorProtocol(Protocol):
    async def validate_devices(
        self, devices: Sequence[BLEDeviceProtocol], timeout: float = 10.0
    ) -> Sequence[DiscoveredDesk]: ...
    async def validate_device(
        self, device: BLEDeviceProtocol, timeout: float = 10.0
    ) -> DiscoveredDesk | None: ...


class DeskValidator:
    """
    Validates BLE desk devices by connecting and checking for required characteristics.

    This validator connects to BLE devices to verify they have the GATT services
    and characteristics expected of supported desk devices.
    """

    def __init__(
        self,
        client_factory: ClientFactory | None = None,
        desk_configs_by_service: dict[str, DeskConfig] | None = None,
    ):
        self._client_factory = client_factory or _create_default_client
        self._desk_configs_by_service = (
            desk_configs_by_service or DESK_CONFIGS_BY_SERVICE
        )

    async def validate_devices(
        self, devices: Sequence[BLEDeviceProtocol], timeout: float = 10.0
    ) -> list[DiscoveredDesk]:
        """
        Validate multiple BLE devices.

        Args:
            devices: Sequence of BLE devices to validate
            timeout: Maximum time in seconds per device

        Returns:
            List of validated desks (non-validated devices are filtered out)
        """
        desks = []
        for device in devices:
            desk = await self.validate_device(
                device=device,
                timeout=timeout,
            )
            if desk:
                desks.append(desk)

        logger.debug(f"Validated {len(desks)} desk(s) from {len(devices)} device(s)")
        return desks

    async def validate_device(
        self, device: BLEDeviceProtocol, timeout: float = 5.0
    ) -> DiscoveredDesk | None:
        # Set on successful validation, returned even if cleanup fails
        discovered_desk = None

        try:
            logger.debug(
                f"Attempting to connect to device {device.address} with timeout of {timeout} second(s)"
            )
            async with self._client_factory(device, timeout) as client:
                if not client.is_connected:
                    logger.warning(f"Failed to connect to device {device.address}")
                    return None

                logger.debug(
                    f"Services found on {device.address}: {[s.uuid for s in client.services]}"
                )

                for service in client.services:
                    if service.uuid not in self._desk_configs_by_service:
                        continue

                    desk_config = self._desk_configs_by_service[service.uuid]
                    if _service_has_required_characteristics(
                        device.address, service, desk_config
                    ):
                        logger.debug(f"Successfully validated device {device.address}")
                        discovered_desk = DiscoveredDesk(
                            address=device.address,
                            name=device.name,
                            desk_config=desk_config,
                        )
                        return discovered_desk

                logger.debug(
                    f"Device {device.address} does not appear to be a supported desk"
                )
                return None

        except EOFError:
            if discovered_desk:
                # Error was encountered while cleaning up the connection, ignore it
                return discovered_desk
            else:
                logger.warning(
                    f"Connection dropped while validating device {device.address}"
                )
                return None
        except TimeoutError:
            logger.warning(
                f"Connection timeout while validating device {device.address}. "
                f"If emulating a GATT service with a smartphone, try pairing first via Bluetooth settings."
            )
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error while validating device {device.address}: {e!r}"
            )
            return None


def _create_default_client(
    device: BLEDeviceProtocol, timeout: float
) -> BLEClientProtocol:
    return BleakClient(address_or_ble_device=device, timeout=timeout)


def _service_has_required_characteristics(
    address: str, gatt_service: GATTServiceProtocol, desk_config: DeskConfig
) -> bool:
    """Check if a service has all required desk characteristics."""

    chars_expected = {
        desk_config.input_char_uuid,
        desk_config.output_char_uuid,
        desk_config.name_char_uuid,
    }
    chars_actual = gatt_characteristics_to_uuids(gatt_service.characteristics)
    chars_found = chars_expected & chars_actual

    if not chars_found:
        logger.warning(
            f"Device {address} has service {gatt_service.uuid} but none of the required characteristics"
        )
        return False

    if chars_found != chars_expected:
        logger.warning(
            f"Device {address} has service {gatt_service.uuid} but characteristics don't match desk profile. "
            f"Expected: {list(chars_expected)}, "
            f"Found: {list(chars_actual)}"
        )
        return False

    return True
