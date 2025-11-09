from unittest.mock import AsyncMock, MagicMock

import pytest

from uplift_ble.desk_finder import DeskFinder
from uplift_ble.models import DiscoveredDesk


class FakeBLEDevice:
    """Fake BLE device for testing."""

    def __init__(self, address: str, name: str | None = None):
        self.address = address
        self.name = name


class TestDeskFinder:
    @pytest.mark.asyncio
    async def test_find_returns_validated_desks(self):
        """find() returns desks that pass validation."""
        mock_scanner = AsyncMock()
        devices = [
            FakeBLEDevice(address="AA:AA:AA:AA:AA:AA", name="Desk 1"),
            FakeBLEDevice(address="BB:BB:BB:BB:BB:BB", name="Desk 2"),
        ]
        mock_scanner.scan.return_value = devices

        mock_validator = AsyncMock()
        validated_desks = [
            DiscoveredDesk(
                address="AA:AA:AA:AA:AA:AA", name="Desk 1", desk_config=MagicMock()
            ),
        ]
        mock_validator.validate_devices.return_value = validated_desks

        finder = DeskFinder(desk_scanner=mock_scanner, desk_validator=mock_validator)
        results = await finder.find(timeout_scanner=5.0, timeout_validator=10.0)
        assert len(results) == 1
        assert results[0].address == "AA:AA:AA:AA:AA:AA"
        mock_scanner.scan.assert_called_once_with(timeout=5.0)
        mock_validator.validate_devices.assert_called_once_with(
            devices=devices, timeout=10.0
        )

    @pytest.mark.asyncio
    async def test_find_returns_empty_when_no_devices_found_by_scanner(self):
        """find() returns empty list when scanner finds no devices."""
        mock_scanner = AsyncMock()
        mock_scanner.scan.return_value = []
        mock_validator = AsyncMock()
        finder = DeskFinder(desk_scanner=mock_scanner, desk_validator=mock_validator)
        results = await finder.find()
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_find_returns_empty_when_no_devices_validate(self):
        """find() returns empty list when devices are found but none validate."""
        mock_scanner = AsyncMock()
        devices = [FakeBLEDevice(address="AA:AA:AA:AA:AA:AA")]
        mock_scanner.scan.return_value = devices
        mock_validator = AsyncMock()
        mock_validator.validate_devices.return_value = []
        finder = DeskFinder(desk_scanner=mock_scanner, desk_validator=mock_validator)
        results = await finder.find()
        assert len(results) == 0
