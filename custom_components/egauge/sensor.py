"""Sensor platform for integration_blueprint."""
import asyncio

from homeassistant import core
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor.const import SensorDeviceClass, SensorStateClass

from . import _LOGGER
from .const import (
    DEFAULT_NAME,
    DOMAIN,
    EGAUGE_DEVICE_CLASS,
    EGAUGE_HISTORICAL,
    EGAUGE_INSTANTANEOUS,
    EGAUGE_UNIT_CONVERSIONS,
    EGAUGE_UNITS,
    HISTORICAL_INTERVALS,
    ICON,
    TODAY,
)
from .entity import EGaugeEntity


async def async_setup_entry(hass: core.HomeAssistant, entry, async_add_devices):
    """Set up sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    inst_registers, hist_registers = await asyncio.gather(
        coordinator.client.get_instantaneous_registers(),
        coordinator.client.get_historical_registers(),
    )
    _LOGGER.debug("Instantaneous registers: %s", inst_registers)
    _LOGGER.debug("Historical registers: %s", hist_registers)
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
        data_type: str,
        register_name,
        register_type_code,
        interval,
        coordinator,
        config_entry,
    ) -> None:
        self.data_type = data_type
        self.register_name = register_name
        self.register_type_code = register_type_code
        self.interval = interval
        self.unit_conversion = EGAUGE_UNIT_CONVERSIONS[self.data_type].get(
            self.register_type_code, 1.0
        )

        _LOGGER.info(
            "register_name: %s  type: %s  register_type_code: %s  interval: %s  "
            "unit_conversion: %s",
            self.register_name,
            self.data_type,
            self.register_type_code,
            self.interval,
            self.unit_conversion,
        )

        super().__init__(coordinator, config_entry)

    @property
    def is_historical(self) -> bool:
        """True if this sensor represents a historical value, false otherwise."""
        return self.data_type == EGAUGE_HISTORICAL

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""
        if self.is_historical:
            return f"{self.entry_id}-{self.interval}-{self.register_name}"
        return f"{self.entry_id}-{self.register_name}"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        if self.is_historical:
            return f"{DEFAULT_NAME} {self.interval} {self.register_name}"
        return f"{DEFAULT_NAME} {self.register_name}"

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        data = self.coordinator.data[self.data_type]
        if self.is_historical:
            data = data[self.interval]
        value = data.get(self.register_name)
        value = value * self.unit_conversion
        if self.state_class == SensorStateClass.TOTAL_INCREASING and value < 0:
            pv = value
            value = abs(value)
            _LOGGER.debug(
                "%s is total_increasing: %s -> %s (%s)",
                self.name,
                pv,
                value,
                f"{value:.2f}",
            )

        return f"{value:.2f}"

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        return {
            "integration": DOMAIN,
            "register_type_code": self.register_type_code,
            "data_type": self.data_type,
        }

    @property
    def unit_of_measurement(self) -> str | None:
        """Return the units of measurement for the entity."""
        return EGAUGE_UNITS[self.data_type].get(self.register_type_code)

    @property
    def device_class(self) -> SensorDeviceClass | None:
        """Return the device class for use by hass."""
        return EGAUGE_DEVICE_CLASS[self.data_type].get(self.register_type_code)

    @property
    def state_class(self) -> SensorStateClass | None:
        """Return the sensor state class for use by hass."""
        if self.data_type == EGAUGE_INSTANTANEOUS:
            return SensorStateClass.MEASUREMENT
        if self.data_type == EGAUGE_HISTORICAL and self.interval == TODAY:
            return SensorStateClass.TOTAL_INCREASING
        return None

    @property
    def icon(self) -> str | None:
        """Return the icon of the sensor."""
        return ICON.get(self.register_type_code)
