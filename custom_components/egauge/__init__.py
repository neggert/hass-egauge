"""
Custom integration to integrate eGauge with Home Assistant.

For more details about this integration, please refer to
https://github.com/neggert/egauge
"""
import logging
from datetime import timedelta

import homeassistant.util.dt as dt_util
from egauge_async import EgaugeClient
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed

from .const import CONF_EGAUGE_URL
from .const import CONF_PASSWORD
from .const import CONF_USERNAME
from .const import DAILY
from .const import DOMAIN
from .const import EGAUGE_HISTORICAL
from .const import EGAUGE_INSTANTANEOUS
from .const import MONTHLY
from .const import SENSOR
from .const import STARTUP_MESSAGE
from .const import TODAY
from .const import WEEKLY
from .const import YEARLY

SCAN_INTERVAL = timedelta(seconds=30)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
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
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, SENSOR))

    entry.add_update_listener(async_reload_entry)
    return True


class EGaugeDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the eGauge API."""

    def __init__(
        self,
        hass: HomeAssistant,
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
            return {
                EGAUGE_INSTANTANEOUS: current_rates,
                EGAUGE_HISTORICAL: historical_data,
            }
        except Exception as exception:
            _LOGGER.warning(f"Exception fetching eGauge data: {exception}")
            raise UpdateFailed() from exception

    def _compute_register_diffs(self, start, end):
        start_vals = {k: r.value for k, r in start.registers.items()}
        end_vals = {k: r.value for k, r in end.registers.items()}
        diff = {k: end_vals[k] - start_vals[k] for k in end_vals.keys()}
        return diff


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    unloaded = await hass.config_entries.async_forward_entry_unload(entry, SENSOR)
    if unloaded:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.client.close()

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
