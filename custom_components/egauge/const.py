"""Constants for eGauge."""
import enum

from homeassistant.const import (
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_PRESSURE,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_VOLTAGE,
    ELECTRICAL_CURRENT_AMPERE,
    ENERGY_KILO_WATT_HOUR,
    PERCENTAGE,
    POWER_WATT,
    PRESSURE_PA,
    TEMP_CELSIUS,
    VOLT,
)

# Base component constants
NAME = "eGauge"
MODEL = "XML API"
DOMAIN = "egauge"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.0"

ISSUE_URL = "https://github.com/neggert/egauge/issues"

# Platforms
SENSOR = "sensor"

# Configuration and options
CONF_ENABLED = "enabled"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_EGAUGE_URL = "egauge_url"

# Defaults
DEFAULT_NAME = DOMAIN

EGAUGE_INSTANTANEOUS = "instantaneous"
EGAUGE_HISTORICAL = "historical"

# Device Classes by eGauge Register Type Code
EGAUGE_DEVICE_CLASS = {
    EGAUGE_INSTANTANEOUS: {
        "h": DEVICE_CLASS_HUMIDITY,
        "T": DEVICE_CLASS_TEMPERATURE,
        "P": DEVICE_CLASS_POWER,
        "Pa": DEVICE_CLASS_PRESSURE,
        "I": DEVICE_CLASS_CURRENT,
        "V": DEVICE_CLASS_VOLTAGE,
    },
    EGAUGE_HISTORICAL: {
        "P": DEVICE_CLASS_ENERGY,
    },
}

EGAUGE_UNITS = {
    EGAUGE_INSTANTANEOUS: {
        "h": PERCENTAGE,
        "T": TEMP_CELSIUS,
        "P": POWER_WATT,
        "Pa": PRESSURE_PA,
        "I": ELECTRICAL_CURRENT_AMPERE,
        "V": VOLT,
    },
    EGAUGE_HISTORICAL: {
        "P": ENERGY_KILO_WATT_HOUR,
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
HISTORICAL_INTERVALS = [DAILY, WEEKLY, MONTHLY, YEARLY]


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
