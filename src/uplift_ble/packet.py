from dataclasses import dataclass
from typing import List


@dataclass
class PacketNotification:
    """
    Represents a notification packet received from the Uplift BLE adapter.
    """

    opcode: int
    payload: bytes
    checksum: int

    def __str__(self) -> str:
        payload_hex = self.payload.hex().upper() if self.payload else ""
        return (
            f"PacketNotification(opcode=0x{self.opcode:02X}, "
            f"payload=0x{payload_hex}, "
            f"checksum=0x{self.checksum:02X})"
        )


def create_command_packet(opcode: int, payload: bytes) -> bytes:
    """
    Creates a packet that represents a command which can be sent to the Uplift BLE adapter.

    The packet format is a special vendor-defined format.

    Frame:
      [0xF1,0xF1] [len] [payload...] [checksum] [0x7E]
    """
    if not 0 <= opcode <= 0xFF:
        raise ValueError("opcode not in range [0,255]")
    payload_len = len(payload)
    if not 0 <= payload_len <= 0xFF:
        raise ValueError("payload length not in range [0,255]")

    checksum = _compute_checksum(opcode, payload)

    return bytes([0xF1, 0xF1, opcode, payload_len, *payload, checksum, 0x7E])


def parse_notification_packets(data: bytes) -> List[PacketNotification]:
    """
    Scan data, which can contain multiple packets, for back-to-back notification packets,
    parsing and returning all valid packets.

    Notification packets are very similar to command packets, except that they
    use the header byte sequence 0xF2F2 instead of 0xF1F1.
    """
    packets: List[PacketNotification] = []
    i = 0
    length = len(data)
    while i + 6 <= length:
        # Look for header
        if data[i : i + 2] != b"\xf2\xf2":
            i += 1
            continue

        # Read length byte
        if i + 4 > length:
            break
        payload_len = data[i + 3]
        total_len = 2 + 1 + 1 + payload_len + 1 + 1

        # Check if full packet present
        if i + total_len > length:
            break

        packet_bytes = data[i : i + total_len]
        p = _parse_notification_packet(packet_bytes)
        if p is not None:
            packets.append(p)
            i += total_len
        else:
            # Skip this header and continue
            i += 1

    return packets


def _parse_notification_packet(data: bytes) -> PacketNotification | None:
    """
    Try to parse a single PacketNotification from exactly one packet in 'data'.
    Returns PacketNotification or None if invalid.
    """
    # Minimum packet length: header(2) + opcode(1) + length(1) + checksum(1) + trailer(1)
    if len(data) < 6:
        return None

    # Header
    if data[0:2] != b"\xf2\xf2":
        return None

    # Trailer
    if data[-1] != 0x7E:
        return None

    opcode = data[2]
    payload_len = data[3]
    expected_total = 2 + 1 + 1 + payload_len + 1 + 1
    if len(data) != expected_total:
        return None

    # Extract payload and checksum
    payload = data[4 : 4 + payload_len]
    checksum = data[-2]

    # Validate checksum
    if _compute_checksum(opcode, payload) != checksum:
        return None

    return PacketNotification(opcode=opcode, payload=payload, checksum=checksum)


def _compute_checksum(opcode: int, payload: bytes) -> int:
    """
    Compute an 8-bit checksum over:
    - opcode byte
    - payload length byte
    - each byte in payload

    Returns (opcode + len(payload) + sum(payload)) mod 256.
    """
    if not 0 <= opcode <= 0xFF:
        raise ValueError("opcode not in range [0,255]")
    total = opcode + len(payload)
    for b in payload:
        total += b
    return total & 0xFF
