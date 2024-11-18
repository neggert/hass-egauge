"""Adds config flow for eGauge."""
from typing import Any

import voluptuous as vol
from egauge_async import EgaugeClient
from homeassistant import config_entries

from . import _LOGGER
from .const import CONF_EGAUGE_URL, CONF_PASSWORD, CONF_USERNAME, DOMAIN


class EGaugeFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for egauge."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self) -> None:
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            valid = await self._test_credentials(
                user_input[CONF_EGAUGE_URL],
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
            )
            if valid:
                return self.async_create_entry(
                    title=user_input[CONF_EGAUGE_URL], data=user_input
                )

            self._errors["base"] = "auth"
            return await self._show_config_form(user_input)

        return await self._show_config_form(user_input)

    async def _show_config_form(
        self,
        user_input: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> config_entries.ConfigFlowResult:
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_EGAUGE_URL, default="http://egaugehq.d.egauge.net"
                    ): str,
                    vol.Optional(CONF_USERNAME, default=""): str,
                    vol.Optional(CONF_PASSWORD, default=""): str,
                }
            ),
            errors=self._errors,
        )

    async def _test_credentials(self, url: str, username: str, password: str) -> bool:
        """Return true if credentials is valid."""
        try:
            client = EgaugeClient(url, username, password)
            await client.get_instantaneous_registers()
            await client.close()
        except Exception:  # noqa: BLE001
            _LOGGER.info("credentials did not validate")
        else:
            return True
        return False
