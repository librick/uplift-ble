from unittest.mock import AsyncMock

import pytest

from uplift_ble.desk_configs import DESK_CONFIGS_BY_SERVICE
from uplift_ble.desk_controller import DeskController
from uplift_ble.desk_enums import DeskEventType, DeskUnit
from uplift_ble.models import DiscoveredDesk
from uplift_ble.packet import parse_notification_packets


def _create_controller(fallback_unit: DeskUnit | None = None) -> DeskController:
    return DeskController(
        client=AsyncMock(),
        input_char_uuid="input",
        output_char_uuid="output",
        requires_wake=False,
        notification_timeout=0,
        fallback_unit=fallback_unit,
    )


@pytest.mark.parametrize(
    ("fallback_unit", "frame", "expected_raw", "expected_height_mm"),
    [
        (
            DeskUnit.CENTIMETERS,
            bytes.fromhex("f2f20103023e0f537e"),
            574,
            574.0,
        ),
        (
            DeskUnit.INCHES,
            bytes.fromhex("f2f2010301370f4b7e"),
            311,
            789.94,
        ),
    ],
)
def test_height_notification_uses_configured_fallback_unit(
    fallback_unit: DeskUnit,
    frame: bytes,
    expected_raw: int,
    expected_height_mm: float,
) -> None:
    controller = _create_controller(fallback_unit)
    reported_heights: list[float] = []
    controller.on(DeskEventType.HEIGHT, reported_heights.append)

    [packet] = parse_notification_packets(frame)
    controller._process_notification_packet(packet)

    assert controller.height_raw == expected_raw
    assert controller.unit is None
    assert controller.height_mm == pytest.approx(expected_height_mm)
    assert reported_heights == pytest.approx([expected_height_mm])


def test_height_notification_remains_unknown_without_unit_or_fallback() -> None:
    controller = _create_controller()
    reported_heights: list[float] = []
    controller.on(DeskEventType.HEIGHT, reported_heights.append)
    [packet] = parse_notification_packets(bytes.fromhex("f2f20103023e0f537e"))

    controller._process_notification_packet(packet)

    assert controller.height_raw == 574
    assert controller.height_mm is None
    assert reported_heights == []


def test_reported_unit_overrides_configured_fallback() -> None:
    controller = _create_controller(DeskUnit.CENTIMETERS)
    [unit_packet] = parse_notification_packets(bytes.fromhex("f2f20e0101107e"))
    [height_packet] = parse_notification_packets(bytes.fromhex("f2f2010301370f4b7e"))

    controller._process_notification_packet(unit_packet)
    controller._process_notification_packet(height_packet)

    assert controller.unit == DeskUnit.INCHES
    assert controller.height_mm == pytest.approx(789.94)


def test_late_reported_unit_corrects_fallback_height() -> None:
    controller = _create_controller(DeskUnit.CENTIMETERS)
    reported_heights: list[float] = []
    controller.on(DeskEventType.HEIGHT, reported_heights.append)
    [height_packet] = parse_notification_packets(bytes.fromhex("f2f2010301370f4b7e"))
    [unit_packet] = parse_notification_packets(bytes.fromhex("f2f20e0101107e"))

    controller._process_notification_packet(height_packet)
    controller._process_notification_packet(unit_packet)

    assert controller.unit == DeskUnit.INCHES
    assert controller.height_mm == pytest.approx(789.94)
    assert reported_heights == pytest.approx([311.0, 789.94])


def test_unit_listener_observes_corrected_fallback_height() -> None:
    controller = _create_controller(DeskUnit.CENTIMETERS)
    observed_state: list[tuple[DeskUnit, float | None]] = []
    controller.on(
        DeskEventType.UNIT,
        lambda unit: observed_state.append((unit, controller.height_mm)),
    )
    [height_packet] = parse_notification_packets(bytes.fromhex("f2f2010301370f4b7e"))
    [unit_packet] = parse_notification_packets(bytes.fromhex("f2f20e0101107e"))

    controller._process_notification_packet(height_packet)
    controller._process_notification_packet(unit_packet)

    assert observed_state[0][0] == DeskUnit.INCHES
    assert observed_state[0][1] == pytest.approx(789.94)


def test_late_reported_unit_does_not_duplicate_matching_height() -> None:
    controller = _create_controller(DeskUnit.CENTIMETERS)
    reported_heights: list[float] = []
    controller.on(DeskEventType.HEIGHT, reported_heights.append)
    [height_packet] = parse_notification_packets(bytes.fromhex("f2f20103023e0f537e"))
    [unit_packet] = parse_notification_packets(bytes.fromhex("f2f20e01000f7e"))

    controller._process_notification_packet(height_packet)
    controller._process_notification_packet(unit_packet)

    assert controller.unit == DeskUnit.CENTIMETERS
    assert controller.height_mm == 574.0
    assert reported_heights == [574.0]


def test_late_reported_unit_emits_first_height_without_fallback() -> None:
    controller = _create_controller()
    reported_heights: list[float] = []
    controller.on(DeskEventType.HEIGHT, reported_heights.append)
    [height_packet] = parse_notification_packets(bytes.fromhex("f2f20103023e0f537e"))
    [unit_packet] = parse_notification_packets(bytes.fromhex("f2f20e01000f7e"))

    controller._process_notification_packet(height_packet)
    controller._process_notification_packet(unit_packet)

    assert controller.height_mm == 574.0
    assert reported_heights == [574.0]


def test_unit_change_does_not_reinterpret_previous_height() -> None:
    controller = _create_controller()
    reported_heights: list[float] = []
    controller.on(DeskEventType.HEIGHT, reported_heights.append)
    [centimeters_packet] = parse_notification_packets(bytes.fromhex("f2f20e01000f7e"))
    [height_packet] = parse_notification_packets(bytes.fromhex("f2f20103023e0f537e"))
    [inches_packet] = parse_notification_packets(bytes.fromhex("f2f20e0101107e"))

    controller._process_notification_packet(centimeters_packet)
    controller._process_notification_packet(height_packet)
    controller._process_notification_packet(inches_packet)

    assert controller.unit == DeskUnit.INCHES
    assert controller.height_mm == 574.0
    assert reported_heights == [574.0]


@pytest.mark.asyncio
async def test_request_units_command_is_unchanged() -> None:
    controller = _create_controller(DeskUnit.CENTIMETERS)

    packet = await controller.request_units()

    assert packet == bytes.fromhex("f1f10e000e7e")
    controller.client.write_gatt_char.assert_awaited_once_with(
        "input", packet, response=False
    )


def test_discovered_desk_applies_fallback_unit() -> None:
    config = DESK_CONFIGS_BY_SERVICE["0000ff00-0000-1000-8000-00805f9b34fb"]
    desk = DiscoveredDesk(address="address", name="desk", desk_config=config)
    controller = desk.create_controller(
        AsyncMock(),
        notification_timeout=0,
        fallback_unit=DeskUnit.CENTIMETERS,
    )
    [packet] = parse_notification_packets(bytes.fromhex("f2f20103023e0f537e"))

    controller._process_notification_packet(packet)

    assert controller.height_mm == 574.0
