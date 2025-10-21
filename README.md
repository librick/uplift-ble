# uplift-ble

Unofficial Python library for controlling Uplift standing desks over Bluetooth Low Energy via the [Uplift BLE adapter](https://www.upliftdesk.com/bluetooth-adapter-for-uplift-desk/).

![Made with Python](https://img.shields.io/badge/Made%20with-Python-3776AB.svg)
![PyPI - Version](https://img.shields.io/pypi/v/uplift-ble)
![GitHub License](https://img.shields.io/github/license/librick/uplift-ble)
[![GitHub issues](https://img.shields.io/github/issues/librick/uplift-ble.svg)](https://github.com/librick/uplift-ble/issues)
![GitHub Repo stars](https://img.shields.io/github/stars/librick/uplift-ble)

Benefits:

- Cross platform (made possible by [Bleak](https://github.com/hbldh/bleak))
- Asynchronous API
- Many supported commands, reverse-engineered directly from the Uplift Android app
- Modern logging via Python's built-in logging module
- Minimal dependencies

*This library is unofficial and is NOT affiliated with the company that makes UPLIFT desks.*

⚠️ **WARNING** ⚠️

This software controls the movement of large heavy things. Do NOT run this code if you are in the vicinity of a desk that you do NOT want to move, or even *suspect* that you *could* be in the vicinity of such a desk. No authentication is required to send commands to an Uplift BLE adapter; any person (or machine) with this code who is within range of an adapter can issue commands to the adapter and move the attached desk. That means if, for example, you run this code in your office full of standing desks, you could injure people or damage property.

**This software is provided “as‑is” without warranties of any kind, express or implied. The authors and maintainers are not responsible for any damage, injury, or malfunction that may result from using this software to control your desk or any other hardware. By using this tool, you agree to assume all risks and liabilities.**

## Compatibility

This library was originally written to support a BLE adapter sold by [Uplift Desk](https://www.upliftdesk.com/) for use with their desks. However, Uplift Desk [whitelabels](https://en.wikipedia.org/wiki/White-label_product) (i.e., puts their branding on) hardware and firmware from a company called [Jiecang](https://www.jiecang.com/). Because several other desk companies also whitelabel Jiecang's products, we suspect that this library *could be* compatible with desks from these other companies.

⚠️ **WARNING** ⚠️

This library uses **undocumented**, **vendor-specific commands** that can access hidden desk functions beyond normal user controls, including minimum/maximum height limits, motor speed, and leg synchronization. **This poses real safety risks.**

Additionally, a command that appears to work safely on one brand (e.g., Uplift Desk) may trigger completely different and potentially dangerous behavior on another brand (e.g., Desky), even if both use Jiecang components. Even within a single brand, different hardware revisions may exist with different behavior. For example, Uplift desks have at least three variants identified by their Bluetooth service UUIDs: 0xFF00, 0xFE60, 0xFF12 (see table columns).

The compatibility table below provides rough guidance based on unofficial feedback from developers, but **we DO NOT guarantee safety or functionality for any desk**. Use this library at your own risk. Always test commands cautiously with the desk clear of obstacles and be prepared to manually stop desk movement.

✅ = Verified working\
⚠️ = Potentially working (proceed with caution)\
🛑 = Verified not working

| Functionality                          | Uplift (0xFF00) | Uplift (0xFE60) | Uplift (0xFF12) | Desky | Omnidesk | Vari | Jarvis | DeskHaus |
| -------------------------------------- | --------------- | --------------- | --------------- | ----- | -------- | ---- | ------ | -------- |
| wake                                   | ⚠️              | ✅              | ⚠️              | ⚠️    | ⚠️       | ⚠️   | ⚠️     | ⚠️       |
| move_up                                | ⚠️              | ✅              | ⚠️              | ⚠️    | ⚠️       | ⚠️   | ⚠️     | ⚠️       |
| move_down                              | ⚠️              | ✅              | ⚠️              | ⚠️    | ⚠️       | ⚠️   | ⚠️     | ⚠️       |
| move_to_height_preset_1                | ⚠️              | ✅              | ⚠️              | ⚠️    | ⚠️       | ⚠️   | ⚠️     | ⚠️       |
| move_to_height_preset_2                | ⚠️              | ✅              | ⚠️              | ⚠️    | ⚠️       | ⚠️   | ⚠️     | ⚠️       |
| request_height_limits                  | ⚠️              | ✅              | ⚠️              | ⚠️    | ⚠️       | ⚠️   | ⚠️     | ⚠️       |
| set_calibration_offset                 | ⚠️              | ✅              | ⚠️              | ⚠️    | ⚠️       | ⚠️   | ⚠️     | ⚠️       |
| set_height_limit_max                   | ⚠️              | ✅              | ⚠️              | ⚠️    | ⚠️       | ⚠️   | ⚠️     | ⚠️       |
| move_to_specified_height               | ⚠️              | ✅              | ⚠️              | ⚠️    | ⚠️       | ⚠️   | ⚠️     | ⚠️       |
| set_current_height_as_height_limit_max | ⚠️              | ✅              | ⚠️              | ⚠️    | ⚠️       | ⚠️   | ⚠️     | ⚠️       |
| set_current_height_as_height_limit_min | ⚠️              | ✅              | ⚠️              | ⚠️    | ⚠️       | ⚠️   | ⚠️     | ⚠️       |
| clear_height_limit_max                 | ⚠️              | ✅              | ⚠️              | ⚠️    | ⚠️       | ⚠️   | ⚠️     | ⚠️       |
| clear_height_limit_min                 | ⚠️              | ✅              | ⚠️              | ⚠️    | ⚠️       | ⚠️   | ⚠️     | ⚠️       |
| stop_movement                          | ⚠️              | ✅              | ⚠️              | ⚠️    | ⚠️       | ⚠️   | ⚠️     | ⚠️       |
| set_units_to_centimeters               | ⚠️              | ✅              | ⚠️              | ⚠️    | ⚠️       | ⚠️   | ⚠️     | ⚠️       |
| set_units_to_inches                    | ⚠️              | ✅              | ⚠️              | ⚠️    | ⚠️       | ⚠️   | ⚠️     | ⚠️       |
| reset                                  | ⚠️              | ✅              | ⚠️              | ⚠️    | ⚠️       | ⚠️   | ⚠️     | ⚠️       |

## Running the CLI

```bash
# Assumes uv is installed
uv sync --group dev
uv run uplift-ble-cli
```

## Reverse Engineering

Valid desk commands were discovered by some combination of the following techniques:

- Reverse-engineered from the source code of the [Uplift Desk App](https://play.google.com/store/apps/details?id=app.android.uplifts&hl=en_US) on Google Play
- Discovered by brute-force search of vendor-specific opcodes against an actual desk
- Referenced from existing work from Bennet Wendorf's [uplift-desk-controller](https://github.com/Bennett-Wendorf/uplift-desk-controller) repo

## Protocol

The [Uplift Desk Bluetooth adapter](https://www.upliftdesk.com/bluetooth-adapter-for-uplift-desk/) uses a proprietary byte-oriented protocol over the Bluetooth Low Energy (BLE) Generic Attribute Profile (GATT). There are two vendor-defined characteristics: one for sending commands to the Bluetooth adapter (`0xFE61`) and one on which notifications are raised such that clients can receive information from the Bluetooth adapter (`0xFE62`).

| GATT Characteristic | Purpose                                                             |
| ------------------- | ------------------------------------------------------------------- |
| 0xFE61              | Desk control. Clients write to this to send commands to the server. |
| 0xFE62              | Desk output. The server sends notifications on this for clients.    |

### Attribute Value Format

All attribute values sent to `0xFE61` (commands) and received from `0xFE62` (notifications) follow the same byte-oriented format. Each attribute value consists of two sync bytes (`0xF1F1` for commands, `0xF2F2` for notifications), an opcode byte, a length byte, an optional payload, a checksum byte, and a terminator byte (always `0x7E`).

#### Attribute Value Format, Commands:

```txt
0xF1 → sync byte, command packet, (1 of 2 bytes)
0xF1 → sync byte, command packet, (2 of 2 bytes)
0xXX → opcode (1 byte)
0xYY → length (1 byte)
0x.. → payload (0xYY byte(s))
0xZZ → (opcode + length + sum of all payload bytes) mod 256
0x7E → terminator (1 byte)
```

#### Attribute Value Format, Notifications:

```txt
0xF2 → sync byte, command packet, (1 of 2 bytes)
0xF2 → sync byte, command packet, (2 of 2 bytes)
0xXX → opcode (1 byte)
0xYY → length (1 byte)
0x.. → payload (0xYY byte(s))
0xZZ → (opcode + length + sum of all payload bytes) mod 256
0x7E → terminator (1 byte)
```

### Known Commands

| Opcode | Length | Attribute Value                           | Purpose                                                                |
| ------ | ------ | ----------------------------------------- | ---------------------------------------------------------------------- |
| 0x01   | 0      | `0xF1,0xF1,0x01,0x00,0x01,0x7E`           | Move desk up                                                           |
| 0x02   | 0      | `0xF1,0xF1,0x02,0x00,0x02,0x7E`           | Move desk down                                                         |
| 0x05   | 0      | `0xF1,0xF1,0x05,0x00,0x05,0x7E`           | Move to height preset 1                                                |
| 0x06   | 0      | `0xF1,0xF1,0x06,0x00,0x06,0x7E`           | Move to height preset 2                                                |
| 0x07   | 0      | `0xF1,0xF1,0x07,0x00,0x07,0x7E`           | Request height limits                                                  |
| 0x10   | 2      | `0xF1,0xF1,0x10,0x02,0xCA,0xFE,0xDB,0x7E` | Set calibration offset                                                 |
| 0x11   | 2      | `0xF1,0xF1,0x11,0x02,0xCA,0xFE,0xDC,0x7E` | Set height limit max                                                   |
| 0x12   | 2      | `0xF1,0xF1,0x12,0x02,0x01,0x00,0x15,0x7E` | Not fully known; potentially dangerous. Sets some configuration value. |
| 0x19   | 1      | `0xF1,0xF1,0x19,0x01,0x00,0x??,0x7E`      | Set touch mode to constant-touch                                       |
| 0x19   | 1      | `0xF1,0xF1,0x19,0x01,0x01,0x??,0x7E`      | Set touch mode to one-touch                                            |
| 0x1B   | 2      | `0xF1,0xF1,0x1B,0x02,0xCA,0xFE,0xE6,0x7E` | Move to specified height                                               |
| 0x21   | 0      | `0xF1,0xF1,0x21,0x00,0x21,0x7E`           | Set current height as height limit max                                 |
| 0x22   | 0      | `0xF1,0xF1,0x22,0x00,0x22,0x7E`           | Set current height as height limit min                                 |
| 0x23   | 1      | `0xF1,0xF1,0x23,0x01,0x01,0x25,0x7E`      | Clear height limit max                                                 |
| 0x23   | 1      | `0xF1,0xF1,0x23,0x01,0x02,0x26,0x7E`      | Clear height limit min                                                 |
| 0x2B   | 0      | `0xF1,0xF1,0x2B,0x00,0x2B,0x7E`           | Stop movement                                                          |
| 0x0E   | 1      | `0xF1,0xF1,0x0E,0x01,0x00,0x0F,0x7E`      | Set units to centimeters                                               |
| 0x0E   | 1      | `0xF1,0xF1,0x0E,0x01,0x01,0x10,0x7E`      | Set units to inches                                                    |
| 0xFE   | 0      | `0xF1,0xF1,0xFE,0x00,0xFE,0x7E`           | Reset                                                                  |

Some of commands above were found by reverse-engineering the Uplift app (v1.1.0) using tools such as JADX. Specifically, the authors read through the .java code for the activities within the `com.jiecang.app.android.aidesk` namespace. Other commands were found by exhaustive search over the range of all opcodes.

### Known Notifications

| Opcode | Payload Length | Purpose                                                                                                          | Factory Value (taken from V2-Commercial model) |
| ------ | -------------- | ---------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| 0x01   | 3              | Reports the height of the desk in 0.1 mm (100 µm) increments. Byte 0: unknown (usually 0x00), Bytes 1-2: height. | Unknown                                        |
| 0x02   | 1              | Reports desk error conditions via single-byte error codes.                                                       | N/A                                            |
| 0x04   | 0              | Seen when the desk is in an error state and the display shows **RST**.                                           | N/A                                            |
| 0x07   | 4              | Reports height limit configuration. Bytes 0-1: max height (mm), Bytes 2-3: min height (mm).                      | Unknown                                        |
| 0x0E   | 1              | Reports display unit preference. 0x00: centimeters, 0x01: inches.                                                | Unknown                                        |
| 0x10   | 2              | Reports the calibration offset in millimeters (2‑byte, big‑endian).                                              | `572`                                          |
| 0x11   | 2              | Reports the max height limit in millimeters (2‑byte, big‑endian).                                                | `671`                                          |
| 0x12   | 2              | Reports some configuration value. The corresponding command is potentially dangerous.                            | Unknown                                        |
| 0x19   | 1              | Reports touch mode. 0x00: one-touch mode, 0x01: constant-touch mode.                                             | Unknown                                        |
| 0x1F   | 1              | Reports lock status. 0x00: unlocked, 0x01: locked.                                                               | Unknown                                        |
| 0x21   | 2              | Reports maximum height limit in millimeters (real-time update, 2‑byte, big‑endian).                              | Unknown                                        |
| 0x22   | 2              | Reports minimum height limit in millimeters (real-time update, 2‑byte, big‑endian).                              | Unknown                                        |
| 0x25   | 2              | Reports height preset 1. Units vary by hardware/firmware. (2‑byte, big‑endian).                                  | Unknown                                        |
| 0x26   | 2              | Reports height preset 2. Units vary by hardware/firmware. (2‑byte, big‑endian).                                  | Unknown                                        |
| 0x27   | 2              | Reports height preset 3. Units vary by hardware/firmware. (2‑byte, big‑endian).                                  | Unknown                                        |
| 0x28   | 2              | Reports height preset 4. Units vary by hardware/firmware. (2‑byte, big‑endian).                                  | Unknown                                        |

There may exist notification packets whose opcodes and payload structures are unknown. PRs are welcome!

### Calibration Offset

The calibration offset adds a fixed offset to the height of the desk.
This table summarizes some examples of what the Desk's display shows for various calibration offsets when the desk is at its lowest point.

| Calibration Offset (mm) | Desk Unit | Display Reading                                               |
| ----------------------- | --------- | ------------------------------------------------------------- |
| 0                       | inches    | 0.01                                                          |
| 254                     | inches    | 10.1                                                          |
| 508                     | inches    | 20.1                                                          |
| 762                     | inches    | 30.1                                                          |
| 2537                    | inches    | 100                                                           |
| 25396                   | inches    | 999                                                           |
| 25397                   | inches    | *Weird state!* Display shows **RST** but desk can still move. |
| 65535                   | inches    | *Weird state!* Display shows **RST** but desk can still move. |

### Error Codes

For the notification with opcode 0x02, the desk reports desk error conditions using a single byte.
This table summarizes known error codes and their meanings.

| Error Code | Summary                        | Troubleshooting                                                                                                             |
| ---------- | ------------------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| E01        | M1 overcurrent protection      | Ensure the total weight capacity of the table has not been exceeded and that no obstacles obstruct the movement.            |
| E02        | M2 overcurrent protection      | Ensure the total weight capacity of the table has not been exceeded and that no obstacles obstruct the movement.            |
| E03        | M3 overcurrent protection      | Ensure the total weight capacity of the table has not been exceeded and that no obstacles obstruct the movement.            |
| E04        | M4 overcurrent protection      | Ensure the total weight capacity of the table has not been exceeded and that no obstacles obstruct the movement.            |
| E05        | Unknown                        | Unknown                                                                                                                     |
| E06        | Unknown                        | Unknown                                                                                                                     |
| E07        | M1 hall error                  | Ensure all columns are properly connected to the control box. Check cables for damage.                                      |
| E08        | M2 hall error                  | Ensure all columns are properly connected to the control box. Check cables for damage.                                      |
| E09        | M3 hall error                  | Ensure all columns are properly connected to the control box. Check cables for damage.                                      |
| E10        | M4 hall error                  | Ensure all columns are properly connected to the control box. Check cables for damage.                                      |
| E11        | Unknown                        | Unknown                                                                                                                     |
| E12        | Unknown                        | Unknown                                                                                                                     |
| E13        | Unknown                        | Unknown                                                                                                                     |
| H01        | Overheat/duty cycle protection | Allow system to rest for 16 minutes, use normally. Follow the duty cycle rating to ensure no issues arise from overheating. |
| H02        | Unknown                        | Unknown                                                                                                                     |
| LOCK       | The desk is locked             | The desk is locked to prevent movement. For supported keypads, unlock it by holding the "M" button.                         |

See https://www.content.upliftdesk.com/content/pdfs/other/V2-ControlBox-Programming.pdf
See https://www.progressivedesk.com/blogs/top-tips/standing-desk-troubleshooting-guide-understanding-error-codes

## Security of the Uplift BLE Adapter

The Bluetooth adapter allows unauthenticated GATT commands to be sent to it (no pairing or encryption required). The Uplift app itself allows you to discover and connect to nearby desks without, for example, a pairing code.

The author thinks this is a bad idea. A malicious actor could write code (possibly using a library such as this one) to scan for nearby desks, connect to them without any explicit authorization, and either soft-brick them through a series of commands designed to make the desk inoperable via the app and physical controller, or move desks when people do not intend for them to be moved.

## Making a New Release

Checkout a branch for the release:

```
git checkout -b release/X.Y.Z
```

Edit `pyproject.toml` and change version to `X.Y.Z` (where `X.Y.Z` is a semver, no "v" prefix):

```
version = "X.Y.Z"
```

Commit the version bump:

```
git add pyproject.toml
git commit -m "chore: bump version to X.Y.Z"
git push origin release/X.Y.Z
```

Create a PR from release/X.Y.Z to main.\
Merge the PR.
Checkout main and pull latest:

```bash
git checkout main
git pull origin main
```

Then create and push a tag:

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

Then create a GitHub release. Choose the tag "vX.Y.Z".\
Generate release notes.\
Click publish.

Publish to PyPI:

```bash
uv build
uv publish

# Clean up
rm -rf dist/ build/
```

## Contributors

[![Contributors](https://contrib.rocks/image?repo=librick/uplift-ble)](https://github.com/librick/uplift-ble/graphs/contributors)

## Prior Work

This project builds on the prior work of Bennett Wendorf's [uplift-desk-controller](https://github.com/Bennett-Wendorf/uplift-desk-controller) repo. In addition to publishing a Python library, they also authored a Home Assistant integration, [hass-uplift-desk](https://github.com/Bennett-Wendorf/hass-uplift-desk). The uplift-ble library was originally intended to be a fork of Bennett's repo, but grew in scope to be a standalone library. I am thankful for Bennett's work and contributions to open source software.

## Legal

This project is an **unofficial project** and is **NOT** endorsed by nor affiliated with the company that makes UPLIFT desks. We make no claims to the trademarks or intellectual property of the UPLIFT company. All code in this repo is written independently of UPLIFT and is MIT licensed. Any vendor-specific information used in this code is discovered through reverse-engineering publicly available information.
