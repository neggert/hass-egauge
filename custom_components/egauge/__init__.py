"""
Custom integration to integrate eGauge with Home Assistant.

For more details about this integration, please refer to
https://github.com/neggert/egauge
"""

import logging
from datetime import timedelta

import homeassistant.util.dt as dt_util
from egauge_async import EgaugeClient
from homeassistant import config_entries, core, exceptions
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_EGAUGE_URL,
    CONF_PASSWORD,
    CONF_USERNAME,
    DAILY,
    DOMAIN,
    EGAUGE_HISTORICAL,
    EGAUGE_INSTANTANEOUS,
    MONTHLY,
    SENSOR,
    STARTUP_MESSAGE,
    TODAY,
    WEEKLY,
    YEARLY,
)

SCAN_INTERVAL = timedelta(seconds=30)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the eGauge Power Meter component."""
    # @TODO: Add setup code.
    return True


# TODO: fix this issue
# Logger: homeassistant.helpers.frame  # noqa: ERA001
# Source: helpers/frame.py:151
# First occurred: 6:02:51 PM (1 occurrences)
# Last logged: 6:02:51 PM
#
# Detected code that calls async_forward_entry_setup for integration egauge with title:
# http://192.168.xx.xxx and entry_id: XXXXXXXXXXXXXXXX, during setup without
# awaiting async_forward_entry_setup, which can cause the setup lock to be released
# before the setup is done. This will stop working in Home Assistant 2025.1. Please
# report this issue.
#
async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    egauge_url = entry.data.get(CONF_EGAUGE_URL)
    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)

    client = EgaugeClient(egauge_url, username, password)

    coordinator = EGaugeDataUpdateCoordinator(
        hass, client=client, update_interval=SCAN_INTERVAL
    )
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise exceptions.ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, [SENSOR])

    entry.add_update_listener(async_reload_entry)
    return True


class EGaugeDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the eGauge API."""

    def __init__(
        self,
        hass: core.HomeAssistant,
        client: EgaugeClient,
        update_interval: timedelta,
    ) -> None:
        """Initialize."""
        self.client = client
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

    async def _async_update_data(self):
        """Update data via library."""
        try:
            current_rates = await self.client.get_current_rates()
            now = dt_util.now()

            # note: these *must* be sorted
            timestamps = [
                now,
                dt_util.start_of_local_day(),
                now - timedelta(days=1),
                now - timedelta(days=7),
                now - timedelta(days=30),
                now - timedelta(days=365),
            ]
            _LOGGER.debug(f"Querying eGauge for timestamps {timestamps}")

            data = await self.client.get_historical_data(timestamps=timestamps)
            _LOGGER.debug(f"eGauge responded with {data}")

            historical_data = {
                TODAY: self._compute_register_diffs(data[1], data[0]),
                DAILY: self._compute_register_diffs(data[2], data[0]),
                WEEKLY: self._compute_register_diffs(data[3], data[0]),
                MONTHLY: self._compute_register_diffs(data[4], data[0]),
                YEARLY: self._compute_register_diffs(data[5], data[0]),
            }
        except Exception as exception:
            _LOGGER.warning(f"Exception fetching eGauge data: {exception}")
            raise UpdateFailed from exception
        else:
            return {
                EGAUGE_INSTANTANEOUS: current_rates,
                EGAUGE_HISTORICAL: historical_data,
            }

    def _compute_register_diffs(self, start, end):
        start_vals = {k: r.value for k, r in start.registers.items()}
        end_vals = {k: r.value for k, r in end.registers.items()}
        return {k: end_vals[k] - start_vals[k] for k in end_vals}


async def async_unload_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Handle removal of an entry."""
    unloaded = await hass.config_entries.async_forward_entry_unload(entry, SENSOR)
    if unloaded:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.client.close()

    return unloaded


async def async_reload_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
