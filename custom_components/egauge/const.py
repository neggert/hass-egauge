"""Constants for eGauge."""
from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfPressure,
    UnitOfTemperature,
)

# Base component constants
DOMAIN = "egauge"
NAME = "eGauge"
MODEL = "XML API"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.0"

ISSUE_URL = "https://github.com/neggert/egauge/issues"

# Platforms
SENSOR = "sensor"

# Configuration and options
CONF_ENABLED = "enabled"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"  # noqa: S105
CONF_EGAUGE_URL = "egauge_url"

# Defaults
DEFAULT_NAME = DOMAIN

EGAUGE_INSTANTANEOUS = "instantaneous"
EGAUGE_HISTORICAL = "historical"
EGAUGE_TODAY = "today"

# Device Classes by eGauge Register Type Code
EGAUGE_DEVICE_CLASS = {
    EGAUGE_INSTANTANEOUS: {
        "h": SensorDeviceClass.HUMIDITY,
        "T": SensorDeviceClass.TEMPERATURE,
        "P": SensorDeviceClass.POWER,
        "Pa": SensorDeviceClass.PRESSURE,
        "I": SensorDeviceClass.CURRENT,
        "V": SensorDeviceClass.VOLTAGE,
    },
    EGAUGE_HISTORICAL: {
        "P": SensorDeviceClass.ENERGY,
    },
}

EGAUGE_UNITS = {
    EGAUGE_INSTANTANEOUS: {
        "h": PERCENTAGE,
        "T": UnitOfTemperature.CELSIUS,
        "P": UnitOfPower.WATT,
        "Pa": UnitOfPressure.PA,
        "I": UnitOfElectricCurrent.AMPERE,
        "V": UnitOfElectricPotential.VOLT,
    },
    EGAUGE_HISTORICAL: {
        "P": UnitOfEnergy.KILO_WATT_HOUR,
    },
}

ICON = {
    "h": "hass:water-percent",
    "T": "hass:thermometer",
    "P": "hass:flash",
    "Pa": "hass:gauge",
    "I": "hass:flash",
    "V": "hass:flash",
}


EGAUGE_UNIT_CONVERSIONS = {
    EGAUGE_INSTANTANEOUS: {},
    EGAUGE_HISTORICAL: {"P": 1 / 3600000},
}


# Intervals for historical data
DAILY = "daily"
WEEKLY = "weekly"
MONTHLY = "monthly"
YEARLY = "yearly"
TODAY = "todays"
HISTORICAL_INTERVALS = [DAILY, WEEKLY, MONTHLY, YEARLY, TODAY]


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
