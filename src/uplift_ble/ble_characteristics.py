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

BLE_CHAR_UUID_GAP_DEVICE_NAME = normalize_uuid_16(0x2A00)
BLE_CHAR_UUID_GAP_APPEARANCE = normalize_uuid_16(0x2A01)
BLE_CHAR_UUID_GAP_PERIPHERAL_PRIVACY_FLAG = normalize_uuid_16(0x2A02)
BLE_CHAR_UUID_GAP_PERIPHERAL_PREFERRED_CONNECTION_PARAMETERS = normalize_uuid_16(0x2A04)

BLE_CHAR_UUID_DIS_MANUFACTURER_NAME = normalize_uuid_16(0x2A29)
BLE_CHAR_UUID_DIS_MODEL_NUMBER = normalize_uuid_16(0x2A24)
BLE_CHAR_UUID_DIS_SERIAL_NUMBER = normalize_uuid_16(0x2A25)
BLE_CHAR_UUID_DIS_HARDWARE_REV = normalize_uuid_16(0x2A27)
BLE_CHAR_UUID_DIS_FIRMWARE_REV = normalize_uuid_16(0x2A26)
BLE_CHAR_UUID_DIS_SOFTWARE_REV = normalize_uuid_16(0x2A28)
BLE_CHAR_UUID_DIS_SYSTEM_ID = normalize_uuid_16(0x2A23)
BLE_CHAR_UUID_DIS_PNP_ID = normalize_uuid_16(0x2A50)

# UUID for sending control commands to the Uplift BLE adapter.
BLE_CHAR_UUID_UPLIFT_DESK_CONTROL: str = normalize_uuid_16(0xFE61)
# UUID for receiving status and output values from the Uplift BLE adapter.
BLE_CHAR_UUID_UPLIFT_DESK_OUTPUT: str = normalize_uuid_16(0xFE62)
