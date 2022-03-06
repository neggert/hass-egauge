"""Sensor platform for integration_blueprint."""
import asyncio

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor import STATE_CLASS_MEASUREMENT
from homeassistant.components.sensor import STATE_CLASS_TOTAL_INCREASING

from . import _LOGGER
from .const import DEFAULT_NAME
from .const import DOMAIN
from .const import EGAUGE_DEVICE_CLASS
from .const import EGAUGE_HISTORICAL
from .const import EGAUGE_INSTANTANEOUS
from .const import EGAUGE_UNIT_CONVERSIONS
from .const import EGAUGE_UNITS
from .const import HISTORICAL_INTERVALS
from .const import ICON
from .const import TODAY
from .entity import EGaugeEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    inst_registers, hist_registers = await asyncio.gather(
        coordinator.client.get_instantaneous_registers(),
        coordinator.client.get_historical_registers(),
    )
    _LOGGER.debug(f"Instantaneous registers: {inst_registers}")
    _LOGGER.debug(f"Historical registers: {hist_registers}")
    devices = [
        EGaugeSensor(
            EGAUGE_INSTANTANEOUS,
            register_name,
            register_type_code,
            None,
            coordinator,
            entry,
        )
        for register_name, register_type_code in inst_registers.items()
    ]
    for interval in HISTORICAL_INTERVALS:
        devices.extend(
            [
                EGaugeSensor(
                    EGAUGE_HISTORICAL,
                    register_name,
                    register_type_code,
                    interval,
                    coordinator,
                    entry,
                )
                for register_name, register_type_code in hist_registers.items()
                if register_type_code in EGAUGE_DEVICE_CLASS[EGAUGE_HISTORICAL]
            ]
        )
    async_add_devices(devices)


class EGaugeSensor(EGaugeEntity, SensorEntity):
    """eGauge Sensor class."""

    def __init__(
        self,
        data_type,
        register_name,
        register_type_code,
        interval,
        coordinator,
        config_entry,
    ):
        self.data_type = data_type
        self.register_name = register_name
        self.register_type_code = register_type_code
        self.interval = interval
        self.unit_conversion = EGAUGE_UNIT_CONVERSIONS[self.data_type].get(
            self.register_type_code, 1.0
        )
        super().__init__(coordinator, config_entry)

    @property
    def is_historical(self):
        return self.data_type == EGAUGE_HISTORICAL

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        if self.is_historical:
            return f"{self.entry_id}-{self.interval}-{self.register_name}"
        else:
            return f"{self.entry_id}-{self.register_name}"

    @property
    def name(self):
        """Return the name of the sensor."""
        if self.is_historical:
            return f"{DEFAULT_NAME} {self.interval} {self.register_name}"
        else:
            return f"{DEFAULT_NAME} {self.register_name}"

    @property
    def state(self):
        """Return the state of the sensor."""
        data = self.coordinator.data[self.data_type]
        if self.is_historical:
            data = data[self.interval]
        value = data.get(self.register_name)
        value = value * self.unit_conversion
        return f"{value:.2f}"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "integration": DOMAIN,
            "register_type_code": self.register_type_code,
            "data_type": self.data_type,
        }

    @property
    def unit_of_measurement(self):
        return EGAUGE_UNITS[self.data_type].get(self.register_type_code)

    @property
    def device_class(self):
        return EGAUGE_DEVICE_CLASS[self.data_type].get(self.register_type_code)

    @property
    def state_class(self):
        if self.data_type == EGAUGE_INSTANTANEOUS:
            return STATE_CLASS_MEASUREMENT
        elif self.data_type == EGAUGE_HISTORICAL and self.interval == TODAY:
            return STATE_CLASS_TOTAL_INCREASING
        return None

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON.get(self.register_type_code)
