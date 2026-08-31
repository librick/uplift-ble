from dataclasses import dataclass

from bleak import BleakClient

from uplift_ble.desk_configs import DeskConfig
from uplift_ble.desk_controller import DeskController
from uplift_ble.desk_enums import DeskUnit


@dataclass
class DiscoveredDesk:
    address: str
    name: str | None
    desk_config: DeskConfig

    def create_controller(
        self,
        client: BleakClient,
        notification_timeout: float = 1.0,
        fallback_unit: DeskUnit | None = None,
    ) -> DeskController:
        """Create a controller for this desk.

        Args:
            client: Connected BLE client used to communicate with the desk.
            notification_timeout: Seconds to wait for notifications after commands.
            fallback_unit: Display unit used only if the desk does not report one.

        Returns:
            A controller configured for the discovered desk profile.
        """
        return DeskController(
            client=client,
            input_char_uuid=self.desk_config.input_char_uuid,
            output_char_uuid=self.desk_config.output_char_uuid,
            requires_wake=self.desk_config.requires_wake,
            notification_timeout=notification_timeout,
            fallback_unit=fallback_unit,
        )
