import re
import click

from uplift_ble.units import convert_cm_to_mm, convert_in_to_mm, round_half_up

UNIT_RE = re.compile(r"^(\d+(?:\.\d+)?)(mm|cm|in)$", re.IGNORECASE)


class HeightParam(click.ParamType):
    name = "height"

    def convert(self, value, param, ctx):
        m = UNIT_RE.fullmatch(value)
        if not m:
            if re.fullmatch(r"^\d+(?:\.\d+)?$", value):
                self.fail(
                    f"{value!r} is missing a unit suffix; expected one of 'mm', 'cm', or 'in'.",
                    param,
                    ctx,
                )
            self.fail(
                f"{value!r} is not a valid height (expected e.g. '64cm', '26.5in', or '660mm')",
                param,
                ctx,
            )

        num_str, unit = m.groups()
        val = float(num_str)
        u = unit.lower()

        if u == "mm":
            mm_val = val
        elif u == "cm":
            mm_val = convert_cm_to_mm(val)
        elif u == "in":
            mm_val = convert_in_to_mm(val)
        else:
            # This should never happen if the regex is correct.
            raise AssertionError(
                f"Internal error: unexpected unit {u!r}. Please report this as a bug."
            )

        return int(round_half_up(mm_val))


HEIGHT = HeightParam()
