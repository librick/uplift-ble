from typing import Any
from unittest.mock import MagicMock

import pytest

from uplift_ble.desk_configs import DeskConfig
from uplift_ble.desk_validator import DeskValidator


class FakeServiceCollection:
    """Fake GATT service collection that matches GATTServiceCollectionProtocol."""

    def __init__(self, services: list[Any]):
        self._services = services

    def __iter__(self):
        return iter(self._services)


class FakeBLEDevice:
    """Fake BLE device that matches BLEDeviceProtocol."""

    def __init__(self, address: str, name: str | None = None):
        self.address = address
        self.name = name


class FakeBLEClient:
    def __init__(self, is_connected: bool, services: list[Any] = None):
        self.is_connected = is_connected
        self.services = FakeServiceCollection(services or [])

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


def create_fake_gatt_service(service_uuid: str, char_uuids: list[str]):
    """Helper to create a fake GATT service with characteristics."""
    service = MagicMock()
    service.uuid = service_uuid
    characteristics = []
    for char_uuid in char_uuids:
        char = MagicMock()
        char.uuid = char_uuid
        characteristics.append(char)

    service.characteristics = characteristics
    return service


class TestDeskValidatorMultipleDevices:
    @pytest.mark.asyncio
    async def test_validate_devices_returns_only_valid_desks(self):
        """Filters out invalid devices and returns only valid desks."""
        desk_config = DeskConfig(
            desk_variant=None,
            service_uuid="service-valid",
            input_char_uuid="char-1",
            output_char_uuid="char-2",
            name_char_uuid="char-3",
        )

        service_valid = create_fake_gatt_service(
            service_uuid="service-valid", char_uuids=["char-1", "char-2", "char-3"]
        )
        service_invalid = create_fake_gatt_service(
            service_uuid="service-invalid", char_uuids=["char-1", "char-2", "char-3"]
        )

        def client_factory(device, timeout):
            match device.address:
                case "AA:AA:AA:AA:AA:AA":
                    return FakeBLEClient(is_connected=True, services=[service_valid])
                case "BB:BB:BB:BB:BB:BB":
                    return FakeBLEClient(is_connected=True, services=[service_invalid])
                case _:
                    raise ValueError(f"Unexpected address: {device.address}")

        validator = DeskValidator(
            client_factory=client_factory,
            desk_configs_by_service={"service-valid": desk_config},
        )

        devices = [
            FakeBLEDevice(address="AA:AA:AA:AA:AA:AA", name="Valid Desk"),
            FakeBLEDevice(address="BB:BB:BB:BB:BB:BB", name="Invalid Desk"),
        ]

        results = await validator.validate_devices(devices, timeout=5.0)
        assert len(results) == 1
        assert results[0].address == "AA:AA:AA:AA:AA:AA"
        assert results[0].name == "Valid Desk"

    @pytest.mark.asyncio
    async def test_validate_devices_returns_empty_list_when_no_valid_desks(self):
        """Returns empty list when no devices are valid."""
        desk_config = DeskConfig(
            desk_variant=None,
            service_uuid="service-1",
            input_char_uuid="char-1",
            output_char_uuid="char-2",
            name_char_uuid="char-3",
        )

        service_invalid = create_fake_gatt_service(
            service_uuid="service-invalid", char_uuids=["char-1"]
        )
        client = FakeBLEClient(is_connected=True, services=[service_invalid])
        validator = DeskValidator(
            client_factory=lambda device, t: client,
            desk_configs_by_service={"service-1": desk_config},
        )

        devices = [
            FakeBLEDevice(address="AA:AA:AA:AA:AA:AA"),
            FakeBLEDevice(address="BB:BB:BB:BB:BB:BB"),
        ]
        results = await validator.validate_devices(devices, timeout=5.0)
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_validate_devices_with_empty_list_returns_empty_list(self):
        """Returns empty list given empty input."""
        validator = DeskValidator()
        results = await validator.validate_devices([], timeout=5.0)
        assert len(results) == 0


class TestDeskValidatorSingleDevice:
    @pytest.mark.asyncio
    async def test_validate_device_when_not_connected_returns_none(self):
        """Device that fails to connect returns None."""
        client = FakeBLEClient(is_connected=False)
        validator = DeskValidator(client_factory=lambda device, t: client)
        device = FakeBLEDevice(address="AA:BB:CC:DD:EE:FF")
        result = await validator.validate_device(device)
        assert result is None

    @pytest.mark.asyncio
    async def test_validate_device_with_valid_service_returns_desk(self):
        """Device with matching service and characteristics returns DiscoveredDesk."""
        desk_config = DeskConfig(
            desk_variant=None,
            service_uuid="service-1",
            input_char_uuid="char-1",
            output_char_uuid="char-2",
            name_char_uuid="char-3",
        )

        fake_service = create_fake_gatt_service(
            service_uuid="service-1", char_uuids=["char-1", "char-2", "char-3"]
        )
        client = FakeBLEClient(is_connected=True, services=[fake_service])
        validator = DeskValidator(
            client_factory=lambda device, t: client,
            desk_configs_by_service={"service-1": desk_config},
        )

        device = FakeBLEDevice(address="AA:BB:CC:DD:EE:FF", name="Test Desk")
        result = await validator.validate_device(device)
        assert result is not None
        assert result.address == "AA:BB:CC:DD:EE:FF"
        assert result.name == "Test Desk"
        assert result.desk_config == desk_config

    @pytest.mark.asyncio
    async def test_validate_device_with_wrong_service_returns_none(self):
        """Device with non-matching service UUID returns None."""
        desk_config = DeskConfig(
            desk_variant=None,
            service_uuid="expected-service",
            input_char_uuid="char-1",
            output_char_uuid="char-2",
            name_char_uuid="char-3",
        )

        fake_service = create_fake_gatt_service(
            service_uuid="wrong-service", char_uuids=["char-1", "char-2", "char-3"]
        )
        client = FakeBLEClient(is_connected=True, services=[fake_service])
        validator = DeskValidator(
            client_factory=lambda device, t: client,
            desk_configs_by_service={"expected-service": desk_config},
        )

        device = FakeBLEDevice(address="AA:BB:CC:DD:EE:FF")
        result = await validator.validate_device(device)
        assert result is None

    @pytest.mark.asyncio
    async def test_validate_device_with_missing_characteristics_returns_none(self):
        """Device missing required characteristics returns None."""
        desk_config = DeskConfig(
            desk_variant=None,
            service_uuid="service-1",
            input_char_uuid="char-1",
            output_char_uuid="char-2",
            name_char_uuid="char-3",
        )
        fake_service = create_fake_gatt_service(
            service_uuid="service-1",
            char_uuids=["char-1", "char-2"],
        )
        client = FakeBLEClient(is_connected=True, services=[fake_service])
        validator = DeskValidator(
            client_factory=lambda device, t: client,
            desk_configs_by_service={"service-1": desk_config},
        )

        device = FakeBLEDevice(address="AA:BB:CC:DD:EE:FF")
        result = await validator.validate_device(device)
        assert result is None
