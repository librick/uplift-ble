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

## Usage

The uplift-ble module includes two main classes, `DeskScanner` and `Desk`. Usage example:

```python
import asyncio
import logging
import sys

from uplift_ble.desk import Desk
from uplift_ble.scanner import DeskScanner


async def main():
    # The `DeskScanner` class is used to discover nearby desk adapters and their Bluetooth MAC addresses.
    devices = await DeskScanner.discover()

    if len(devices) == 0:
        print("Error: no desks found.", file=sys.stderr)
        sys.exit(1)
    elif len(devices) > 1:
        print("Error: multiple desks found. Exiting for safety.", file=sys.stderr)
        sys.exit(1)

    # The `Desk` class represents a desk and supports the async context manager API.
    async with Desk(address=devices[0].address) as desk:
        height_before_move = await desk.get_current_height()
        await desk.move_up()
        height_after_move = await desk.get_current_height()
        print(
            f"Moved desk from height of {height_before_move} mm to {height_after_move} mm"
        )

    print("Done.")


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )


if __name__ == "__main__":
    _configure_logging()
    asyncio.run(main())

```


## CLI Utility (uplift_ble_cli.py)

### Prerequisites

* Python 3.11 or higher
* Git

### Installation

These instructions are intended for Linux users but are likely broadly applicable.

1. **Clone the Repository**
   ```bash
   git clone git@github.com:librick/uplift-ble.git
   cd uplift-ble
    ```
2. **Create & Activate Virtual Environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3. **Verify Virtual Environment**
    ```bash
    which python3
    ```
4. **Install Dependencies**
    ```bash
    python3 -m pip install .
    ```
5. **Install Test Dependencies and Run Tests (Optional)**
    ```bash
    python3 -m pip install -e ".[test]"
    python3 -m pytest -v
    ```
6. **Run the CLI**
    ```bash
    python3 scripts/uplift_ble_cli.py --help
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
|--------|--------|-------------------------------------------| -----------------------------------------------------------------------|
| 0x01   | 0      | `0xF1,0xF1,0x01,0x00,0x01,0x7E`           | Move desk up                                                           |
| 0x02   | 0      | `0xF1,0xF1,0x02,0x00,0x02,0x7E`           | Move desk down                                                         |
| 0x05   | 0      | `0xF1,0xF1,0x05,0x00,0x05,0x7E`           | Move to height preset 1                                                |
| 0x06   | 0      | `0xF1,0xF1,0x06,0x00,0x06,0x7E`           | Move to height preset 2                                                |
| 0x07   | 0      | `0xF1,0xF1,0x07,0x00,0x07,0x7E`           | Request height limits                                                  |
| 0x10   | 2      | `0xF1,0xF1,0x10,0x02,0xCA,0xFE,0xDB,0x7E` | Set calibration offset                                                 |
| 0x11   | 2      | `0xF1,0xF1,0x11,0x02,0xCA,0xFE,0xDC,0x7E` | Set height limit max                                                   |
| 0x12   | 2      | `0xF1,0xF1,0x12,0x02,0x01,0x00,0x15,0x7E` | Not fully known; potentially dangerous. Sets some configuration value. |
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

| Opcode | Payload Length | Purpose                                                                               | Factory Value (taken from V2-Commercial model) |
|--------|----------------|---------------------------------------------------------------------------------------|------------------------------------------------|
| 0x01   |       3        | Reports the height of the desk in 0.01 mm (10 µm) increments.                         | Unknown                                        |
| 0x04   |       0        | Seen when the desk is in an error state and the display shows **RST**.                | N/A                                            |
| 0x10   |       2        | Reports the calibration offset in millimeters (2‑byte, big‑endian).                   | `572`                                          |
| 0x11   |       2        | Reports the max height limit in millimeters (2‑byte, big‑endian).                     | `671`                                          |
| 0x12   |       2        | Reports some configuration value. The corresponding command is potentially dangerous. | Unknown                                        |
| 0x25   |       2        | Reports height preset 1. Units vary by hardware/firmware. (2‑byte, big‑endian).       | Unknown                                        |
| 0x26   |       2        | Reports height preset 2. Units vary by hardware/firmware. (2‑byte, big‑endian).       | Unknown                                        |
| 0x27   |       2        | Reports height preset 3. Units vary by hardware/firmware. (2‑byte, big‑endian).       | Unknown                                        |
| 0x28   |       2        | Reports height preset 4. Units vary by hardware/firmware. (2‑byte, big‑endian).       | Unknown                                        |

Most notification packets seem to have opcodes that match the opcode of an associated command packet.
For example, sending the command packet with opcode=0x01 triggers a notification packet with the same opcode,
containing the desk's current height.

**There are many notification packets whose opcodes and payload structures are unknown. PRs are welcome!**

### Explaining the Calibration Offset
The calibration offset adds a fixed offset to the height of the desk.
This table summarizes some examples of what the Desk's display shows for various calibration offsets when the desk is at its lowest point.

| Calibration Offset (mm) | Desk Unit | Display Reading                                                      |
|-------------------------|-----------|----------------------------------------------------------------------|
| 0                       | inches    | 0.01                                                                 |
| 254                     | inches    | 10.1                                                                 |
| 508                     | inches    | 20.1                                                                 |
| 762                     | inches    | 30.1                                                                 |
| 2537                    | inches    | 100                                                                  |
| 25396                   | inches    | 999                                                                  |
| 25397                   | inches    | *Weird state!* Display shows **RST** but desk can still move.        |
| 65535                   | inches    | *Weird state!* Display shows **RST** but desk can still move.        |


## Security of the Uplift BLE Adapter
The Bluetooth adapter allows unauthenticated GATT commands to be sent to it (no pairing or encryption required). The Uplift app itself allows you to discover and connect to nearby desks without, for example, a pairing code.

The author thinks this is a bad idea. A malicious actor could easily write code (or use a library such as this one) to scan for nearby desks, connect to them without any explicit authorization, and either soft-brick them through a series of commands designed to make the desk impossible to move via the app or physical controller (see example below), or move desks when people do not intend for them to be moved.

## Contributors
[![Contributors](https://contrib.rocks/image?repo=librick/uplift-ble)](https://github.com/librick/uplift-ble/graphs/contributors)

## Prior Work
This project builds on the prior work of Bennett Wendorf's [uplift-desk-controller](https://github.com/Bennett-Wendorf/uplift-desk-controller) repo. In addition to publishing a Python library, they also authored a Home Assistant integration, [hass-uplift-desk](https://github.com/Bennett-Wendorf/hass-uplift-desk). The uplift-ble library was originally intended to be a fork of Bennett's repo, but grew in scope to be a standalone library. I am thankful for Bennett's work and contributions to open source software.

## Legal
This project is an **unofficial project** and is **NOT** endorsed by nor affiliated with the company that makes UPLIFT desks. We make no claims to the trademarks or intellectual property of the UPLIFT company. All code in this repo is written independently of UPLIFT and is MIT licensed. Any vendor-specific information used in this code is discovered through reverse-engineering publicly available information.
