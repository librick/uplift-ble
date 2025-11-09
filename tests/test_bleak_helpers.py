from unittest.mock import Mock

import pytest

from uplift_ble.ble_helpers import (
    gatt_characteristics_to_uuids,
)


class TestGattCharacteristicsToUUIDs:
    """Test suite for gatt_characteristics_to_uuids function."""

    def test_characteristics_len_0(self):
        """Test with empty collection of characteristics."""
        result = gatt_characteristics_to_uuids([])
        assert result == set()

    def test_characteristics_len_1(self):
        """Test with a single GATT characteristic."""
        mock_char = Mock()
        mock_char.uuid = "00002a00-0000-1000-8000-00805f9b34fb"
        result = gatt_characteristics_to_uuids([mock_char])
        assert result == {"00002a00-0000-1000-8000-00805f9b34fb"}

    def test_characteristics_len_3(self):
        """Test with multiple GATT characteristics."""
        char1 = Mock()
        char1.uuid = "00002a00-0000-1000-8000-00805f9b34fb"
        char2 = Mock()
        char2.uuid = "00002a01-0000-1000-8000-00805f9b34fb"
        char3 = Mock()
        char3.uuid = "00002a04-0000-1000-8000-00805f9b34fb"
        characteristics = [char1, char2, char3]
        result = gatt_characteristics_to_uuids(characteristics)
        expected = {
            "00002a00-0000-1000-8000-00805f9b34fb",
            "00002a01-0000-1000-8000-00805f9b34fb",
            "00002a04-0000-1000-8000-00805f9b34fb",
        }
        assert result == expected

    def test_works_with_tuple(self):
        """Test that function works with tuple input."""
        char1 = Mock()
        char1.uuid = "00002a00-0000-1000-8000-00805f9b34fb"
        char2 = Mock()
        char2.uuid = "00002a01-0000-1000-8000-00805f9b34fb"
        result = gatt_characteristics_to_uuids(
            (
                char1,
                char2,
            )
        )
        assert result == {char1.uuid, char2.uuid}

    def test_works_with_generator(self):
        """Test that function works with generator input."""
        char1 = Mock()
        char1.uuid = "00002a00-0000-1000-8000-00805f9b34fb"
        char2 = Mock()
        char2.uuid = "00002a01-0000-1000-8000-00805f9b34fb"

        def char_generator():
            yield char1
            yield char2

        result = gatt_characteristics_to_uuids(char_generator())
        assert result == {char1.uuid, char2.uuid}

    def test_different_uuid_formats(self):
        """Test with different UUID formats (short and long UUIDs)."""
        char1 = Mock()
        char1.uuid = "2a00"
        char2 = Mock()
        char2.uuid = "00002a01-0000-1000-8000-00805f9b34fb"
        char3 = Mock()
        char3.uuid = "custom-uuid-67890"
        characteristics = [char1, char2, char3]
        result = gatt_characteristics_to_uuids(characteristics)
        expected = {"2a00", "00002a01-0000-1000-8000-00805f9b34fb", "custom-uuid-67890"}
        assert result == expected

    def test_duplicates_ignored(self):
        """Test that duplicate UUIDs are handled correctly (set behavior)."""
        uuid_1 = "00002a00-0000-1000-8000-00805f9b34fb"
        uuid_2 = "00002a01-0000-1000-8000-00805f9b34fb"
        char1 = Mock()
        char1.uuid = uuid_1
        char2 = Mock()
        char2.uuid = uuid_1
        char3 = Mock()
        char3.uuid = uuid_2
        characteristics = [char1, char2, char3]
        result = gatt_characteristics_to_uuids(characteristics)
        assert result == {uuid_1, uuid_2}

    def test_none_characteristic_raises_error(self):
        """Test that None characteristic raises ValueError."""
        char1 = Mock()
        char1.uuid = "00002a00-0000-1000-8000-00805f9b34fb"
        characteristics = [char1, None]
        with pytest.raises(ValueError, match="Characteristic cannot be None"):
            gatt_characteristics_to_uuids(characteristics)

    @pytest.mark.parametrize(
        "uuid_value,expected_type",
        [
            (None, "NoneType"),
            (12345, "int"),
            ([], "list"),
            ({}, "dict"),
        ],
    )
    def test_non_string_uuid_raises_error(self, uuid_value, expected_type):
        """Test that non-string UUIDs raise ValueError."""
        char = Mock()
        char.uuid = uuid_value
        with pytest.raises(
            ValueError, match=f"UUID must be a string, got {expected_type}"
        ):
            gatt_characteristics_to_uuids([char])
