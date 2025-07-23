#!/usr/bin/env python3
"""
CLI to test the uplift_ble module.
"""

import asyncio
import json
import logging

import click
import typer
from typing import Optional

from param_type_height import HEIGHT
from param_type_mac_address import MAC_ADDRESS
from uplift_ble import units
from uplift_ble.desk import Desk
from uplift_ble.scanner import DeskScanner

logging.basicConfig(level=logging.INFO)
app = typer.Typer(help="uplift-ble command line tool for controlling with uplift desks")


def _resolve_address(address: Optional[str], timeout: float) -> str:
    """
    If address is provided, return it; otherwise discover desks and
    ensure exactly one before returning that address.
    """
    if address:
        return address
    typer.echo("No address provided, scanning for Uplift desks…")
    addresses = asyncio.run(DeskScanner.discover(timeout))
    if not addresses:
        typer.echo("Error: no uplift desks found.")
        raise typer.Exit(code=1)
    if len(addresses) > 1:
        typer.echo(
            f"Error: multiple desks found ({len(addresses)}). Please specify one explicitly."
        )
        for addr in addresses:
            typer.echo(f"- {addr}")
        raise typer.Exit(code=1)
    return addresses[0]


def _check_manual_reset(ctx: typer.Context, param, value: bool) -> bool:
    """
    Callback for the --danger-requires-manual-reset flag.
    Exits unless the flag was passed.
    """
    if not value:
        name = ctx.info_name
        typer.echo(
            f"Error: `{name}` will leave the desk in a state that requires manual reset.\n"
            "If you really want to do this, re-run with --danger-requires-manual-reset."
        )
        ctx.exit(1)
    return value


def manual_reset_option() -> typer.Option:
    """
    Shared option for commands that require manual reset confirmation.

    Some commands put the desk in a reset state and cause the display to show "ASR".
    The desk will not accept additional commands in this state. For these, we require an explicit flag to prevent
    a situation where a user sends a command remotely (e.g., by using a Bluetooth proxy)
    and locks themselves out by issuing a command that makes the desk inoperable without an in-person reset.
    """
    return typer.Option(
        False,
        "--danger-requires-manual-reset",
        help="⚠️ Desk will require a manual, in-person reset after this. Must be passed to proceed.",
        callback=_check_manual_reset,
    )


@app.command()
def discover(timeout: float = typer.Option(5.0, help="Discovery duration in seconds")):
    """
    Discover nearby Uplift desks by BLE service UUID.
    """
    addresses = asyncio.run(DeskScanner.discover(timeout))
    if not addresses:
        typer.echo("No uplift desks found.")
        raise typer.Exit(code=1)
    typer.echo("Discovered Uplift desk addresses:")
    for addr in addresses:
        typer.echo(f"- {addr}")


@app.command()
def listen(
    ctx: typer.Context,
):
    """
    Listen continuously for notifications from the desk and print parsed packets.
    """
    timeout = ctx.obj["timeout"]
    addr = _resolve_address(ctx.obj["address"], timeout)
    typer.echo(
        f"Listening for notifications on {addr} with a timeout of {timeout} second(s) (Ctrl-C to stop)…"
    )

    async def _listen():
        async with Desk(addr) as desk:
            while True:
                await asyncio.sleep(0.1)

    try:
        asyncio.run(_listen())
    except KeyboardInterrupt:
        typer.echo("Stopped listening.")


@app.command()
def get_device_information(ctx: typer.Context):
    """
    Get standard BLE device information service (DIS) values.

    This implementation is non-exhaustive. It only returns information
    for a few well-known, standard characteristics.
    If you think your device supports non-standard characteristics within the standard service,
    consider using a different tool to dump the values of all readable characteristics.
    """
    address = _resolve_address(ctx.obj["address"], ctx.obj["timeout"])
    requires_wake = ctx.obj["requires_wake"]
    device_info = asyncio.run(Desk(address, requires_wake).get_device_information())
    typer.echo(json.dumps(device_info, indent=4, ensure_ascii=False))


@app.command()
def get_current_height(ctx: typer.Context):
    """
    Get the most recently-received desk height.
    """
    address = _resolve_address(ctx.obj["address"], ctx.obj["timeout"])
    requires_wake = ctx.obj["requires_wake"]
    height_mm = asyncio.run(Desk(address, requires_wake).get_current_height())
    if height_mm is None:
        typer.echo("Error: failed to retrieve current height")
        raise typer.Exit(code=1)
    else:
        height_in = units.convert_mm_to_in(mm=height_mm)
        typer.echo(
            f"Received current desk height: {height_mm} mm, approx {height_in} inches."
        )


@app.callback()
def common_options(
    ctx: typer.Context,
    address: Optional[str] = typer.Option(
        None,
        "-a",
        "--address",
        click_type=MAC_ADDRESS,
        help="Bluetooth address of the desk",
    ),
    timeout: float = typer.Option(
        5.0,
        "-t",
        "--timeout",
        click_type=click.FloatRange(min=0.0),
        help="Timeout for discovery when address omitted",
    ),
    requiresWake: bool = typer.Option(
        False,
        "-w",
        "--requires-wake",
        help="If set, send wake commands prior to subsequent commands",
    ),
):
    """
    Common options injected for commands requiring a desk address.
    """
    ctx.obj = {
        "address": address,
        "timeout": timeout,
        "requires_wake": requiresWake,
    }


@app.command()
def move_up(ctx: typer.Context):
    """
    Move the desk up.
    """
    address = _resolve_address(ctx.obj["address"], ctx.obj["timeout"])
    requires_wake = ctx.obj["requires_wake"]
    packet = asyncio.run(Desk(address, requires_wake).move_up())
    typer.echo(f"Sent {ctx.info_name} packet to {address}: {packet.hex()}")


@app.command()
def move_down(ctx: typer.Context):
    """
    Move the desk down.
    """
    address = _resolve_address(ctx.obj["address"], ctx.obj["timeout"])
    requires_wake = ctx.obj["requires_wake"]
    packet = asyncio.run(Desk(address, requires_wake).move_down())
    typer.echo(f"Sent {ctx.info_name} packet to {address}: {packet.hex()}")


@app.command()
def request_height_limits(ctx: typer.Context):
    """
    Request height limits from the desk.
    """
    address = _resolve_address(ctx.obj["address"], ctx.obj["timeout"])
    requires_wake = ctx.obj["requires_wake"]
    packet = asyncio.run(Desk(address, requires_wake).request_height_limits())
    typer.echo(f"Sent {ctx.info_name} packet to {address}: {packet.hex()}")


@app.command()
def set_calibration_offset(
    ctx: typer.Context,
    calibration_offset: int = typer.Argument(..., help="Calibration offset (0-65535)"),
    danger_requires_manual_reset: bool = manual_reset_option(),
):
    """
    Set the calibration offset.
    """
    address = _resolve_address(ctx.obj["address"], ctx.obj["timeout"])
    requires_wake = ctx.obj["requires_wake"]
    packet = asyncio.run(
        Desk(address, requires_wake).set_calibration_offset(calibration_offset)
    )
    typer.echo(f"Sent {ctx.info_name} packet to {address}: {packet.hex()}")


@app.command()
def set_height_limit_max(
    ctx: typer.Context,
    max_height: int = typer.Argument(..., help="Maximum height limit (0-65535)"),
    danger_requires_manual_reset: bool = manual_reset_option(),
):
    """
    Set the maximum height limit.
    """
    address = _resolve_address(ctx.obj["address"], ctx.obj["timeout"])
    requires_wake = ctx.obj["requires_wake"]
    packet = asyncio.run(Desk(address, requires_wake).set_height_limit_max(max_height))
    typer.echo(f"Sent {ctx.info_name} packet to {address}: {packet.hex()}")


@app.command()
def move_to_specified_height(
    ctx: typer.Context,
    height: int = typer.Argument(
        ..., click_type=HEIGHT, help="Target height (0-65535)"
    ),
):
    """
    Move the desk to a specified height.
    """
    address = _resolve_address(ctx.obj["address"], ctx.obj["timeout"])
    requires_wake = ctx.obj["requires_wake"]
    packet = asyncio.run(Desk(address, requires_wake).move_to_specified_height(height))
    typer.echo(f"Sent {ctx.info_name} packet to {address}: {packet.hex()}")


@app.command()
def set_current_height_as_height_limit_max(ctx: typer.Context):
    """
    Set current height as the maximum height limit.
    """
    address = _resolve_address(ctx.obj["address"], ctx.obj["timeout"])
    requires_wake = ctx.obj["requires_wake"]
    packet = asyncio.run(
        Desk(address, requires_wake).set_current_height_as_height_limit_max()
    )
    typer.echo(f"Sent {ctx.info_name} packet to {address}: {packet.hex()}")


@app.command()
def set_current_height_as_height_limit_min(ctx: typer.Context):
    """
    Set current height as the minimum height limit.
    """
    address = _resolve_address(ctx.obj["address"], ctx.obj["timeout"])
    requires_wake = ctx.obj["requires_wake"]
    packet = asyncio.run(
        Desk(address, requires_wake).set_current_height_as_height_limit_min()
    )
    typer.echo(f"Sent {ctx.info_name} packet to {address}: {packet.hex()}")


@app.command()
def clear_height_limit_max(ctx: typer.Context):
    """
    Clear the maximum height limit.
    """
    address = _resolve_address(ctx.obj["address"], ctx.obj["timeout"])
    requires_wake = ctx.obj["requires_wake"]
    packet = asyncio.run(Desk(address, requires_wake).clear_height_limit_max())
    typer.echo(f"Sent {ctx.info_name} packet to {address}: {packet.hex()}")


@app.command()
def clear_height_limit_min(ctx: typer.Context):
    """
    Clear the minimum height limit.
    """
    address = _resolve_address(ctx.obj["address"], ctx.obj["timeout"])
    requires_wake = ctx.obj["requires_wake"]
    packet = asyncio.run(Desk(address, requires_wake).clear_height_limit_min())
    typer.echo(f"Sent {ctx.info_name} packet to {address}: {packet.hex()}")


@app.command()
def stop_movement(ctx: typer.Context):
    """
    Stop desk movement.
    """
    address = _resolve_address(ctx.obj["address"], ctx.obj["timeout"])
    requires_wake = ctx.obj["requires_wake"]
    packet = asyncio.run(Desk(address, requires_wake).stop_movement())
    typer.echo(f"Sent {ctx.info_name} packet to {address}: {packet.hex()}")


@app.command()
def set_units_to_centimeters(
    ctx: typer.Context,
    danger_requires_manual_reset: bool = manual_reset_option(),
):
    """
    Set units to centimeters.
    """
    address = _resolve_address(ctx.obj["address"], ctx.obj["timeout"])
    requires_wake = ctx.obj["requires_wake"]
    packet = asyncio.run(Desk(address, requires_wake).set_units_to_centimeters())
    typer.echo(f"Sent {ctx.info_name} packet to {address}: {packet.hex()}")


@app.command()
def set_units_to_inches(
    ctx: typer.Context,
    danger_requires_manual_reset: bool = manual_reset_option(),
):
    """
    Set units to inches.
    """
    address = _resolve_address(ctx.obj["address"], ctx.obj["timeout"])
    requires_wake = ctx.obj["requires_wake"]
    packet = asyncio.run(Desk(address, requires_wake).set_units_to_inches())
    typer.echo(f"Sent {ctx.info_name} packet to {address}: {packet.hex()}")


@app.command()
def reset(ctx: typer.Context):
    """
    Reset the desk.
    """
    address = _resolve_address(ctx.obj["address"], ctx.obj["timeout"])
    requires_wake = ctx.obj["requires_wake"]
    packet = asyncio.run(Desk(address, requires_wake).reset())
    typer.echo(f"Sent {ctx.info_name} packet to {address}: {packet.hex()}")


if __name__ == "__main__":
    app()
