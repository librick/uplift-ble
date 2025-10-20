import re
import sys

import click

MAC_RE = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$")
UUID_RE = re.compile(r"^[0-9A-Fa-f]{8}-?[0-9A-Fa-f]{4}-?[0-9A-Fa-f]{4}-?[0-9A-Fa-f]{4}-?[0-9A-Fa-f]{12}$")

class MACAddress(click.ParamType):
    name = "mac_address"

    def convert(self, value, param, ctx):
        if value is None:
            return None

        if MAC_RE.match(value):
            if sys.platform == "darwin":
                self.fail(f"macOS requires uuid addresses, not mac addresses, got {value.lower()}")
            return value.lower()

        if UUID_RE.match(value):
            return value.lower()

        self.fail(f"{value!r} is not a valid MAC address", param, ctx)


MAC_ADDRESS = MACAddress()
