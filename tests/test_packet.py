import pytest

from uplift_ble.packet import (
    _compute_checksum,
    create_command_packet,
    parse_notification_packets,
)


def test_opcode_out_of_range_negative():
    with pytest.raises(ValueError) as exc:
        create_command_packet(-1, b"")
    assert "opcode not in range" in str(exc.value)


def test_opcode_out_of_range_too_large():
    with pytest.raises(ValueError) as exc:
        create_command_packet(0x100, b"")
    assert "opcode not in range" in str(exc.value)


def test_payload_length_too_large():
    with pytest.raises(ValueError) as exc:
        create_command_packet(0, bytes(256))
    assert "payload length not in range" in str(exc.value)


def test_command_packet_opcode_0x00_empty_payload():
    packet = create_command_packet(0x00, b"")
    expected = bytes([0xF1, 0xF1, 0x00, 0x00, 0x00, 0x7E])
    assert packet == expected


def test_command_packet_opcode_0x01_empty_payload():
    """
    Tests construction of the move desk up command
    (`0xF1,0xF1,0x01,0x00,0x01,0x7E`).
    """
    packet = create_command_packet(0x01, b"")
    expected = bytes([0xF1, 0xF1, 0x01, 0x00, 0x01, 0x7E])
    assert packet == expected


def test_command_packet_opcode_0x02_empty_payload():
    """
    Tests construction of the move desk down command
    (`0xF1,0xF1,0x02,0x00,0x02,0x7E`).
    """
    packet = create_command_packet(0x02, b"")
    expected = bytes([0xF1, 0xF1, 0x02, 0x00, 0x02, 0x7E])
    assert packet == expected


def test_command_packet_opcode_0xFE_empty_payload():
    """
    Tests construction of the reset command
    (`0xF1,0xF1,0xFE,0x00,0xFE,0x7E`).
    """
    packet = create_command_packet(0xFE, b"")
    expected = bytes([0xF1, 0xF1, 0xFE, 0x00, 0xFE, 0x7E])
    assert packet == expected


@pytest.mark.parametrize(
    "payload,expected",
    [
        # Command to set height limit max to 0 mm.
        (bytes([0x00, 0x00]), bytes([0xF1, 0xF1, 0x11, 0x02, 0x00, 0x00, 0x13, 0x7E])),
        # Command to set height limit max to 2^{16}-1 mm.
        (bytes([0xFF, 0xFF]), bytes([0xF1, 0xF1, 0x11, 0x02, 0xFF, 0xFF, 0x11, 0x7E])),
        # Command to set height limit max to 1372 mm (approximately 54 inches) in big-endian format.
        (bytes([0x05, 0x5C]), bytes([0xF1, 0xF1, 0x11, 0x02, 0x05, 0x5C, 0x74, 0x7E])),
        # Command to set height limit max to 1422 mm (approximately 56 inches) in big-endian format.
        (bytes([0x05, 0x8E]), bytes([0xF1, 0xF1, 0x11, 0x02, 0x05, 0x8E, 0xA6, 0x7E])),
        # Command to set height limit max to 1473 mm (approximately 58 inches) in big-endian format.
        (bytes([0x05, 0xC1]), bytes([0xF1, 0xF1, 0x11, 0x02, 0x05, 0xC1, 0xD9, 0x7E])),
    ],
)
def test_command_packet_opcode_0x11_two_byte_payload(payload: bytes, expected: bytes):
    """
    Tests construction of the command to set the desk's max height limit.
    """
    packet = create_command_packet(0x11, payload)
    assert packet == expected


@pytest.mark.parametrize(
    "payload,expected",
    [
        # Command to move to height of 0 mm.
        (bytes([0x00, 0x00]), bytes([0xF1, 0xF1, 0x1B, 0x02, 0x00, 0x00, 0x1D, 0x7E])),
        # Command to move to height of 2^{16}-1 mm.
        (bytes([0xFF, 0xFF]), bytes([0xF1, 0xF1, 0x1B, 0x02, 0xFF, 0xFF, 0x1B, 0x7E])),
        # Command to move to height of 1372 mm (approximately 54 inches) in big-endian format.
        (bytes([0x05, 0x5C]), bytes([0xF1, 0xF1, 0x1B, 0x02, 0x05, 0x5C, 0x7E, 0x7E])),
        # Command to move to height of 1422 mm (approximately 56 inches) in big-endian format.
        (bytes([0x05, 0x8E]), bytes([0xF1, 0xF1, 0x1B, 0x02, 0x05, 0x8E, 0xB0, 0x7E])),
        # Command to move to height of 1473 mm (approximately 58 inches) in big-endian format.
        (bytes([0x05, 0xC1]), bytes([0xF1, 0xF1, 0x1B, 0x02, 0x05, 0xC1, 0xE3, 0x7E])),
    ],
)
def test_command_packet_opcode_0x1B_two_byte_payload(payload: bytes, expected: bytes):
    """
    Tests construction of the command to move the desk to a specified height.
    """
    packet = create_command_packet(0x1B, payload)
    assert packet == expected


@pytest.mark.parametrize(
    "payload,expected",
    [
        # Command to set units to centimeters.
        (bytes([0x00]), bytes([0xF1, 0xF1, 0x0E, 0x01, 0x00, 0x0F, 0x7E])),
        # Command to set units to inches.
        (bytes([0x01]), bytes([0xF1, 0xF1, 0x0E, 0x01, 0x01, 0x10, 0x7E])),
    ],
)
def test_command_packet_opcode_0x0E_one_byte_payload(payload: bytes, expected: bytes):
    """
    Tests construction of the command to set the units of the desk.
    """
    packet = create_command_packet(0x0E, payload)
    assert packet == expected


def test_compute_checksum_opcode_out_of_range_negative():
    with pytest.raises(ValueError) as exc:
        _compute_checksum(-1, b"")
    assert "opcode not in range" in str(exc.value)


def test_compute_checksum_opcode_out_of_range_too_large():
    with pytest.raises(ValueError) as exc:
        _compute_checksum(0x100, b"")
    assert "opcode not in range" in str(exc.value)


# One preset query (0x07) response captured from an official UPLIFT V3 adapter
# advertising service 0x00FF: only the first notification carries both 0xF2 bytes.
CAPTURED_PRESET_BURST = [
    "f2f2250202b9e27e",
    "f2260202ec167e",
    "f2270203e6127e",
    "f228020434627e",
]


def test_parse_notification_accepts_captured_short_headers():
    packets = [
        packet
        for frame in CAPTURED_PRESET_BURST
        for packet in parse_notification_packets(bytes.fromhex(frame))
    ]
    assert [(p.opcode, int.from_bytes(p.payload, "big")) for p in packets] == [
        (0x25, 697),
        (0x26, 748),
        (0x27, 998),
        (0x28, 1076),
    ]


def test_parse_notification_reads_back_to_back_short_headers():
    data = bytes.fromhex("".join(CAPTURED_PRESET_BURST))
    assert len(parse_notification_packets(data)) == len(CAPTURED_PRESET_BURST)


def test_parse_notification_rejects_short_header_with_bad_checksum():
    assert parse_notification_packets(bytes.fromhex("f2260202ec177e")) == []
