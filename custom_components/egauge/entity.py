"""Representation of an eGauge entity."""
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    _DataUpdateCoordinatorT,
)

from .const import DOMAIN, MODEL, NAME


class EGaugeEntity(CoordinatorEntity):
    def __init__(self, coordinator: _DataUpdateCoordinatorT, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self.entry_id = self.config_entry.entry_id

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.entry_id)},
            "name": NAME,
            "model": MODEL,
            "manufacturer": NAME,
        }
