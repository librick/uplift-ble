"""
BLE GATT Service UUIDs for the Uplift adapter.

The Uplift BLE adapter's service IDs are 16-bit values chosen from the Bluetooth SIG's
vendor-specific block (0xFE00-0xFEFF). SIG reserves this range for all vendor-assigned
attributes (services, characteristics, and descriptors). Each 16-bit ID is embedded
into the Base UUID template (0000XXXX-0000-1000-8000-00805F9B34FB) to create a
full 128-bit UUID. See Bluetooth SIG Assigned Numbers for details:
https://www.bluetooth.com/specifications/assigned-numbers/
"""

from bleak.uuids import normalize_uuid_16

# UUID for a service which allows clients to discover nearby Uplift adapters.
BLE_SERVICE_UUID_UPLIFT_DISCOVERY: str = normalize_uuid_16(0xFE60)
