from collections.abc import Iterable

from uplift_ble.ble_protos import GATTCharacteristicProtocol


def gatt_characteristics_to_uuids(
    gatt_characteristics: Iterable[GATTCharacteristicProtocol],
) -> set[str]:
    """Extract UUIDs from a collection of GATT characteristics.

    Args:
        gatt_characteristics: An iterable collection of BleakGATTCharacteristic objects.

    Returns:
        A set of UUID strings extracted from the characteristics.

    Raises:
        ValueError: If a characteristic is None or if a characteristic's UUID is not a string.
    """
    uuids = set()
    for char in gatt_characteristics:
        if char is None:
            raise ValueError("Characteristic cannot be None")
        if not isinstance(char.uuid, str):
            raise ValueError(f"UUID must be a string, got {type(char.uuid).__name__}")
        uuids.add(char.uuid)
    return uuids
