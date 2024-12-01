from datetime import datetime
from unittest.mock import AsyncMock, patch

from homeassistant.core import HomeAssistant
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.egauge import async_unload_entry
from custom_components.egauge.const import (
    DAILY,
    DOMAIN,
    EGAUGE_HISTORICAL,
    EGAUGE_INSTANTANEOUS,
    MONTHLY,
    TODAY,
    WEEKLY,
    YEARLY,
)

from .const import MOCK_CONFIG


@pytest.mark.asyncio
async def test_instantaneous_sensor_creation(
    hass: HomeAssistant, bypass_get_registers, bypass_get_data
):
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")

    with patch(
        "egauge_async.EgaugeClient.get_instantaneous_registers"
    ) as get_registers, patch(
        "custom_components.egauge.EGaugeDataUpdateCoordinator._async_update_data",
        new_callable=AsyncMock,
    ) as update:
        get_registers.return_value = {"power_register": "P"}
        update.return_value = {EGAUGE_INSTANTANEOUS: {"power_register": 1234}}
        config_entry.add_to_hass(hass)
        await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

        registry = hass.helpers.entity_registry.async_get()
        assert "sensor.egauge_power_register" in registry.entities

        state = hass.states.get("sensor.egauge_power_register")
        assert state
        assert state.state == "1234.00"
        assert dict(state.attributes) == {
            "integration": DOMAIN,
            "register_type_code": "P",
            "data_type": EGAUGE_INSTANTANEOUS,
            "device_class": "power",
            "state_class": "measurement",
            "friendly_name": "egauge power_register",
            "unit_of_measurement": "W",
            "icon": "hass:flash",
        }

    assert await async_unload_entry(hass, config_entry)


@pytest.mark.asyncio
async def test_historical_sensor_creation(
    hass: HomeAssistant, bypass_get_registers, bypass_get_data
):
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")

    with patch(
        "egauge_async.EgaugeClient.get_historical_registers"
    ) as get_registers, patch(
        "custom_components.egauge.EGaugeDataUpdateCoordinator._async_update_data",
        new_callable=AsyncMock,
    ) as update, patch(
        "homeassistant.util.dt.start_of_local_day"
    ) as start_of_day:
        get_registers.return_value = {"power_register": "P"}
        update.return_value = {
            EGAUGE_HISTORICAL: {
                DAILY: {"power_register": 1 * 3600000},
                WEEKLY: {"power_register": 2 * 3600000},
                MONTHLY: {"power_register": 3 * 3600000},
                YEARLY: {"power_register": 4 * 3600000},
                TODAY: {"power_register": 5 * 3600000},
            }
        }
        dt = datetime(2020, 1, 1)
        start_of_day.return_value = dt
        config_entry.add_to_hass(hass)
        await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

        registry = hass.helpers.entity_registry.async_get()
        assert "sensor.egauge_daily_power_register" in registry.entities
        assert "sensor.egauge_weekly_power_register" in registry.entities
        assert "sensor.egauge_monthly_power_register" in registry.entities
        assert "sensor.egauge_yearly_power_register" in registry.entities
        assert "sensor.egauge_todays_power_register" in registry.entities

        state = hass.states.get("sensor.egauge_daily_power_register")
        assert state
        assert state.state == "1.00"
        assert dict(state.attributes) == {
            "integration": DOMAIN,
            "register_type_code": "P",
            "data_type": EGAUGE_HISTORICAL,
            "device_class": "energy",
            "friendly_name": "egauge daily power_register",
            "unit_of_measurement": "kWh",
            "icon": "hass:flash",
        }

        state = hass.states.get("sensor.egauge_todays_power_register")
        assert state
        assert state.state == "5.00"
        assert dict(state.attributes) == {
            "integration": DOMAIN,
            "register_type_code": "P",
            "data_type": EGAUGE_HISTORICAL,
            "device_class": "energy",
            "state_class": "total_increasing",
            "friendly_name": "egauge todays power_register",
            "unit_of_measurement": "kWh",
            "icon": "hass:flash",
        }

    assert await async_unload_entry(hass, config_entry)
