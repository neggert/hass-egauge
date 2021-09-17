"""Constants for eGauge."""
from homeassistant.const import DEVICE_CLASS_CURRENT
from homeassistant.const import DEVICE_CLASS_ENERGY
from homeassistant.const import DEVICE_CLASS_HUMIDITY
from homeassistant.const import DEVICE_CLASS_POWER
from homeassistant.const import DEVICE_CLASS_PRESSURE
from homeassistant.const import DEVICE_CLASS_TEMPERATURE
from homeassistant.const import DEVICE_CLASS_VOLTAGE
from homeassistant.const import ELECTRIC_CURRENT_AMPERE
from homeassistant.const import ELECTRIC_POTENTIAL_VOLT
from homeassistant.const import ENERGY_KILO_WATT_HOUR
from homeassistant.const import PERCENTAGE
from homeassistant.const import POWER_WATT
from homeassistant.const import PRESSURE_PA
from homeassistant.const import TEMP_CELSIUS

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
EGAUGE_TODAY = "today"

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
        "I": ELECTRIC_CURRENT_AMPERE,
        "V": ELECTRIC_POTENTIAL_VOLT,
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
