try:
    import click
    import typer
except ImportError as e:
    e.add_note("    Note: uplift-ble is missing some dependencies for CLI functionality.")
    e.add_note(
        "    To fix: install uplift-ble with the cli extra: 'uplift-ble[cli]'."
        " Example: 'pip install uplift-ble[cli]'"
    )

    raise e from None

from .uplift_ble_cli import app

__all__ = ["app"]
