from collections.abc import Iterator
from typing import Protocol


class GATTCharacteristicProtocol(Protocol):
    """Protocol for GATT characteristics."""

    @property
    def uuid(self) -> str: ...


class GATTServiceProtocol(Protocol):
    """Protocol for GATT services."""

    @property
    def uuid(self) -> str: ...
    @property
    def characteristics(self) -> list[GATTCharacteristicProtocol]: ...


class GATTServiceCollectionProtocol(Protocol):
    """Protocol for GATT service collections."""

    def __iter__(self) -> Iterator[GATTServiceProtocol]: ...


class BLEClientProtocol(Protocol):
    """Protocol defining the interface for BLE clients."""

    @property
    def is_connected(self) -> bool: ...

    @property
    def services(self) -> GATTServiceCollectionProtocol: ...

    async def __aenter__(self) -> "BLEClientProtocol": ...
    async def __aexit__(self, *args) -> None: ...


class BLEDeviceProtocol(Protocol):
    @property
    def name(self) -> str | None: ...

    @property
    def address(self) -> str: ...
