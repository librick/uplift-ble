import pytest

from uplift_ble.packet import _compute_checksum, create_command_packet


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
