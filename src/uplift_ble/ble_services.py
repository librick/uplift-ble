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

# UUID for the BLE Generic Access Service (GAP).
BLE_SERVICE_UUID_GENERIC_ACCESS_SERVICE: str = normalize_uuid_16(0x1800)
# UUID for the BLE Device Information Service (DIS).
BLE_SERVICE_UUID_DEVICE_INFORMATION_SERVICE: str = normalize_uuid_16(0x180A)
# UUID for vendor-specific discovery service. Based on reverse-engineered Uplift app code.
BLE_SERVICE_UUID_UPLIFT_DISCOVERY_LIERDA_V1: str = normalize_uuid_16(0xFF12)
# UUID for vendor-specific discovery service. Based on reverse-engineered Uplift app code.
BLE_SERVICE_UUID_UPLIFT_DISCOVERY_LIERDA_V2: str = normalize_uuid_16(0xFE60)
