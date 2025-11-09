import asyncio
import functools
import logging
import platform
import sys
from contextlib import asynccontextmanager
from importlib.metadata import PackageNotFoundError, version

import click
from bleak import BleakClient

from uplift_ble.desk_controller import DeskController
from uplift_ble.desk_enums import (
    DeskClearHeightLimit,
    DeskEventType,
    DeskTouchMode,
    DeskUnit,
)
from uplift_ble.desk_finder import DeskFinder
from uplift_ble.models import DiscoveredDesk
from uplift_ble_cli.param_type_height import HEIGHT
from uplift_ble_cli.param_type_mac_address import MAC_ADDRESS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logging.getLogger("uplift_ble").setLevel(logging.DEBUG)
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("bleak").setLevel(logging.WARNING)


@click.group()
@click.option(
    "--address",
    "-a",
    type=MAC_ADDRESS,
    help="Desk BLE address (e.g., AA:BB:CC:DD:EE:FF)",
)
@click.pass_context
def cli(ctx, address):
    """Control standing desks using Bluetooth"""
    ctx.ensure_object(dict)
    ctx.obj["address"] = address


async def _find_desk(
    address: str | None = None,
) -> DiscoveredDesk | None:
    click.echo("Scanning for desks...", err=True)
    desk_finder = DeskFinder()
    desks = await desk_finder.find()

    if not desks:
        click.echo("Error: No desks found", err=True)
        return None

    if address:
        for desk in desks:
            if desk.address.lower() == address.lower():
                click.echo(f"Found matching desk at {desk.address}", err=True)
                return desk

        # No match found
        available = [d.address for d in desks]
        click.echo(f"Error: No desk found at address {address}", err=True)
        click.echo(f"Found {len(desks)} desk(s) at other addresses:", err=True)
        for addr in available:
            click.echo(f"  - {addr}", err=True)
        return None

    # No address specified, require exactly one desk
    if len(desks) == 1:
        desk = desks[0]
        click.echo(f"Found desk at {desk.address}", err=True)
        return desk

    # Multiple desks found
    click.echo(f"Error: Found {len(desks)} desks. Please specify --address", err=True)
    click.echo("Available desks:", err=True)
    for d in desks:
        click.echo(f"  - {d.address}", err=True)
    return None


def _register_notification_handlers(controller: DeskController):
    """Register handlers for all desk event types to log notifications"""

    def make_handler(event_type: DeskEventType):
        def handler(*args):
            if args:
                click.echo(f"Got notification: {event_type.name} - {args}", err=True)
            else:
                click.echo(f"Got notification: {event_type.name}", err=True)

        return handler

    for event_type in DeskEventType:
        controller.on(event_type, make_handler(event_type))


@asynccontextmanager
async def _get_desk_controller(address: str | None):
    desk = await _find_desk(address=address)
    if desk is None:
        sys.exit(1)

    click.echo(f"Connecting to {desk.address}...", err=True)
    async with BleakClient(desk.address) as client:
        if not client.is_connected:
            click.echo(f"Error: Failed to connect to {desk.address}", err=True)
            sys.exit(1)

        click.echo("Connected successfully", err=True)
        async with desk.create_controller(client) as controller:
            _register_notification_handlers(controller)
            yield controller


def with_desk_controller(func):
    @click.pass_context
    @functools.wraps(func)
    def wrapper(ctx, *args, **kwargs):
        address = ctx.obj["address"]

        async def execute():
            async with _get_desk_controller(address) as controller:
                return await func(controller, *args, **kwargs)

        return asyncio.run(execute())

    return wrapper


@cli.command()
def about():
    """Show package versions and high-level system information."""
    packages = ["uplift_ble", "bleak"]

    for package in packages:
        try:
            pkg_version = version(package)
            click.echo(f"{package} version: {pkg_version}")
        except PackageNotFoundError:
            click.echo(f"{package} version: not available")

    click.echo(f"python: {sys.version.split()[0]} ({platform.python_implementation()})")
    click.echo(f"architecture: {platform.machine()}")
    click.echo(f"platform: {platform.platform()}")


@cli.command()
def find():
    """Find nearby desks."""

    async def run():
        desk_finder = DeskFinder()
        desks = await desk_finder.find()

        if not desks:
            click.echo("No desks found", err=True)
            return

        click.echo(f"Found {len(desks)} desk(s):", err=True)
        for desk in desks:
            click.echo(
                f"  - {desk.address} ({desk.name or 'unnamed'}) {desk.desk_config.desk_variant}",
                err=True,
            )

    asyncio.run(run())


@cli.command()
@with_desk_controller
async def wake(controller: DeskController):
    """Send a special wake packet to the desk."""
    await controller.wake()
    click.echo("Sent command to wake up desk", err=True)


@cli.command()
@with_desk_controller
async def move_up(controller: DeskController):
    """Move the desk up relative to its current position."""
    await controller.move_up()
    click.echo("Sent command to move desk up", err=True)


@cli.command()
@with_desk_controller
async def move_down(controller: DeskController):
    """Move the desk down relative to its current position."""
    await controller.move_down()
    click.echo("Sent command to move desk down", err=True)


@cli.command()
@with_desk_controller
async def move_to_height_preset_1(controller: DeskController):
    """Move the desk to programmed height preset 1."""
    await controller.move_to_height_preset_1()
    click.echo("Sent command to move desk to height preset 1", err=True)


@cli.command()
@with_desk_controller
async def move_to_height_preset_2(controller: DeskController):
    """Move the desk to programmed height preset 2."""
    await controller.move_to_height_preset_2()
    click.echo("Sent command to move desk to height preset 2", err=True)


@cli.command()
@with_desk_controller
async def request_height_limits(controller: DeskController):
    """Request the desk's current height limits."""
    await controller.request_height_limits()
    click.echo("Sent command to request desk's current height limits", err=True)


@cli.command()
@click.argument("calibration_offset", type=click.IntRange(0, 0xFFFF))
@with_desk_controller
async def set_calibration_offset(controller: DeskController, calibration_offset: int):
    """Set the calibration offset of the desk."""
    await controller.set_calibration_offset(calibration_offset)
    click.echo(
        f"Sent command to set desk calibration offset to {calibration_offset}", err=True
    )


@cli.command()
@click.argument("max_height", type=click.IntRange(0, 0xFFFF))
@with_desk_controller
async def set_height_limit_max(controller: DeskController, max_height: int):
    """Set the desk's max height limit."""
    await controller.set_height_limit_max(max_height)
    click.echo(f"Sent command to set desk height limit max to {max_height}", err=True)


@cli.command()
@click.argument("touch_mode", type=click.Choice(["one-touch", "constant-touch"]))
@with_desk_controller
async def set_touch_mode(controller: DeskController, touch_mode: str):
    """Set the desk's touch mode to one-touch or constant-touch."""
    match touch_mode:
        case "one-touch":
            await controller.set_touch_mode(DeskTouchMode.ONE_TOUCH)
            click.echo("Sent command to set touch mode to one-touch", err=True)
        case "constant-touch":
            await controller.set_touch_mode(DeskTouchMode.CONSTANT_TOUCH)
            click.echo("Sent command to set touch mode to constant-touch", err=True)
        case _:
            raise ValueError(f"Unexpected touch mode value: {touch_mode}")


@cli.command()
@click.argument("height", type=HEIGHT)
@with_desk_controller
async def move_to_specified_height(controller: DeskController, height: int):
    """Move the desk to a specified height."""
    await controller.move_to_specified_height(height)
    click.echo(f"Sent command to move desk to specified height {height}", err=True)


@cli.command(name="set-curr-height-as-limit-max")
@with_desk_controller
async def set_current_height_as_height_limit_max(controller: DeskController):
    """Save the desk's current height as its maximum height."""
    await controller.set_current_height_as_height_limit_max()
    click.echo("Sent command to set current height as height limit max", err=True)


@cli.command(name="set-curr-height-as-limit-min")
@with_desk_controller
async def set_current_height_as_height_limit_min(controller: DeskController):
    """Save the desk's current height as its minimum height."""
    await controller.set_current_height_as_height_limit_min()
    click.echo("Sent command to set current height as height limit min", err=True)


@cli.command()
@with_desk_controller
async def clear_height_limit_max(controller: DeskController):
    """Clear any saved maximum height limit."""
    await controller.clear_height_limit(limit=DeskClearHeightLimit.MAX)
    click.echo("Sent command to clear height limit max", err=True)


@cli.command()
@with_desk_controller
async def clear_height_limit_min(controller: DeskController):
    """Clear any saved minimum height limit."""
    await controller.clear_height_limit(limit=DeskClearHeightLimit.MIN)
    click.echo("Sent command to clear height limit min", err=True)


@cli.command()
@with_desk_controller
async def stop_movement(controller: DeskController):
    """Stop moving the desk."""
    await controller.stop_movement()
    click.echo("Sent command to stop desk movement", err=True)


@cli.command()
@click.argument("unit", type=click.Choice(["cm", "in"]))
@with_desk_controller
async def set_units(controller: DeskController, unit: str):
    """Set the desk's units to centimeters (cm) or inches (in)."""
    match unit:
        case "cm":
            await controller.set_units(DeskUnit.CENTIMETERS)
            click.echo("Sent command to set units to centimeters", err=True)
        case "in":
            await controller.set_units(DeskUnit.INCHES)
            click.echo("Sent command to set units to inches", err=True)
        case _:
            raise ValueError(f"Unexpected unit value: {unit}")


@cli.command()
@with_desk_controller
async def reset(controller: DeskController):
    """Reset the desk."""
    await controller.reset()
    click.echo("Sent command to reset desk", err=True)


def main():
    cli()


if __name__ == "__main__":
    main()
