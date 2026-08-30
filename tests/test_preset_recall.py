from unittest.mock import AsyncMock

import pytest

from uplift_ble.desk_controller import DeskController
from uplift_ble.desk_enums import DeskEventType
from uplift_ble.packet import parse_notification_packets


def _create_controller() -> DeskController:
    return DeskController(
        client=AsyncMock(),
        input_char_uuid="input",
        output_char_uuid="output",
        requires_wake=False,
        notification_timeout=0,
    )


@pytest.mark.parametrize(
    ("method_name", "opcode"),
    [
        ("move_to_height_preset_3", 0x27),
        ("move_to_height_preset_4", 0x28),
    ],
)
@pytest.mark.asyncio
async def test_preset_recall_commands(method_name: str, opcode: int) -> None:
    controller = _create_controller()

    packet = await getattr(controller, method_name)()

    assert packet == bytes([0xF1, 0xF1, opcode, 0x00, opcode, 0x7E])
    controller.client.write_gatt_char.assert_awaited_once_with(
        "input", packet, response=False
    )


@pytest.mark.parametrize(
    ("frame", "event_type", "property_name", "expected_height"),
    [
        (
            bytes.fromhex("f2f227020408357e"),
            DeskEventType.HEIGHT_PRESET_3,
            "height_preset_3",
            1032,
        ),
        (
            bytes.fromhex("f2f228020433617e"),
            DeskEventType.HEIGHT_PRESET_4,
            "height_preset_4",
            1075,
        ),
    ],
)
def test_height_preset_notifications_remain_supported(
    frame: bytes,
    event_type: DeskEventType,
    property_name: str,
    expected_height: int,
) -> None:
    controller = _create_controller()
    reported_heights: list[int] = []
    controller.on(event_type, reported_heights.append)

    [packet] = parse_notification_packets(frame)
    controller._process_notification_packet(packet)

    assert getattr(controller, property_name) == expected_height
    assert reported_heights == [expected_height]
