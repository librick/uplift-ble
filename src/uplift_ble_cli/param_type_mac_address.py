import re

import click

MAC_RE = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$")


class MACAddress(click.ParamType):
    name = "mac_address"

    def convert(self, value, param, ctx):
        if value is None:
            return None
        if MAC_RE.match(value):
            return value.lower()
        self.fail(f"{value!r} is not a valid MAC address", param, ctx)


MAC_ADDRESS = MACAddress()
