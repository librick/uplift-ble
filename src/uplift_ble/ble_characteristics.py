"""
BLE GATT Characteristic UUIDs for the Uplift adapter.

The Uplift BLE adapter's characteristic IDs are 16-bit values chosen from the Bluetooth SIG's
vendor-specific block (0xFE00-0xFEFF). SIG reserves this range for all vendor-assigned
attributes (services, characteristics, and descriptors). Each 16-bit ID is embedded
into the Base UUID template (0000XXXX-0000-1000-8000-00805F9B34FB) to create a
full 128-bit UUID. See Bluetooth SIG Assigned Numbers for details:
https://www.bluetooth.com/specifications/assigned-numbers/
"""

from bleak.uuids import normalize_uuid_16


# UUID for sending control commands to the Uplift BLE adapter.
BLE_CHAR_UUID_UPLIFT_DESK_CONTROL: str = normalize_uuid_16(0xFE61)

# UUID for receiving status and output values from the Uplift BLE adapter.
BLE_CHAR_UUID_UPLIFT_DESK_OUTPUT: str = normalize_uuid_16(0xFE62)
