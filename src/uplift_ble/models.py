from dataclasses import dataclass

from bleak import BleakClient

from uplift_ble.desk_configs import DeskConfig
from uplift_ble.desk_controller import DeskController


@dataclass
class DiscoveredDesk:
    address: str
    name: str | None
    desk_config: DeskConfig

    def create_controller(
        self, client: BleakClient, notification_timeout: float = 1.0
    ) -> DeskController:
        """Create a controller for this desk."""
        return DeskController(
            client=client,
            input_char_uuid=self.desk_config.input_char_uuid,
            output_char_uuid=self.desk_config.output_char_uuid,
            requires_wake=self.desk_config.requires_wake,
            notification_timeout=notification_timeout,
            command_sync_bytes=self.desk_config.command_sync_bytes,
            notification_sync_bytes=self.desk_config.notification_sync_bytes,
            height_scale_factor=self.desk_config.height_scale_factor,
        )
