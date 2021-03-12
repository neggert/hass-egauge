from unittest.mock import patch, AsyncMock

from homeassistant.core import HomeAssistant

from custom_components.egauge import async_setup_entry, async_unload_entry
from custom_components.egauge.const import (
    DAILY,
    DOMAIN,
    EGAUGE_HISTORICAL,
    EGAUGE_INSTANTANEOUS,
    MONTHLY,
    WEEKLY,
    YEARLY,
)
from custom_components.egauge.sensor import EGaugeSensor

from pytest_homeassistant_custom_component.common import MockConfigEntry

from .const import MOCK_CONFIG


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
        assert await async_setup_entry(hass, config_entry)
        await hass.async_block_till_done()

        registry = await hass.helpers.entity_registry.async_get_registry()
        assert "sensor.egauge_power_register" in registry.entities

        state = hass.states.get("sensor.egauge_power_register")
        assert state
        assert state.state == "1234"
        assert dict(state.attributes) == {
            "integration": DOMAIN,
            "register_type_code": "P",
            "data_type": EGAUGE_INSTANTANEOUS,
            "device_class": "power",
            "friendly_name": "egauge power_register",
            "unit_of_measurement": "W",
            "icon": "hass:flash",
        }

    assert await async_unload_entry(hass, config_entry)


async def test_historical_sensor_creation(
    hass: HomeAssistant, bypass_get_registers, bypass_get_data
):
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")

    with patch(
        "egauge_async.EgaugeClient.get_historical_registers"
    ) as get_registers, patch(
        "custom_components.egauge.EGaugeDataUpdateCoordinator._async_update_data",
        new_callable=AsyncMock,
    ) as update:
        get_registers.return_value = {"power_register": "P"}
        update.return_value = {
            EGAUGE_HISTORICAL: {
                DAILY: {"power_register": 1 * 3600000},
                WEEKLY: {"power_register": 2 * 3600000},
                MONTHLY: {"power_register": 3 * 3600000},
                YEARLY: {"power_register": 4 * 3600000},
            }
        }
        assert await async_setup_entry(hass, config_entry)
        await hass.async_block_till_done()

        registry = await hass.helpers.entity_registry.async_get_registry()
        assert "sensor.egauge_daily_power_register" in registry.entities
        assert "sensor.egauge_weekly_power_register" in registry.entities
        assert "sensor.egauge_monthly_power_register" in registry.entities
        assert "sensor.egauge_yearly_power_register" in registry.entities

        state = hass.states.get("sensor.egauge_daily_power_register")
        assert state
        assert state.state == "1"
        assert dict(state.attributes) == {
            "integration": DOMAIN,
            "register_type_code": "P",
            "data_type": EGAUGE_HISTORICAL,
            "device_class": "energy",
            "friendly_name": "egauge daily power_register",
            "unit_of_measurement": "kWh",
            "icon": "hass:flash",
        }

    assert await async_unload_entry(hass, config_entry)
