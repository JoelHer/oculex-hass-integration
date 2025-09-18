from homeassistant import config_entries
from homeassistant.core import HomeAssistant
import voluptuous as vol
from .const import DOMAIN, CONF_HOST, CONF_PORT, CONF_API_KEY
from .api import EOESApi
import logging
_LOGGER = logging.getLogger(__name__)

class EOESConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            api = EOESApi(user_input[CONF_HOST], user_input[CONF_PORT], user_input.get(CONF_API_KEY))
            try:
                await api.get_streams()
                await api.close()
                return self.async_create_entry(title="Oculex", data=user_input)
            except Exception:
                errors["base"] = "cannot_connect"
                await api.close()

        schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PORT, default=8000): int,
            vol.Optional(CONF_API_KEY): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
