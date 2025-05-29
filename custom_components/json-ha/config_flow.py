from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, DEFAULT_URL
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import async_timeout
import logging

_LOGGER = logging.getLogger(__name__)

class JsonHaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    def __init__(self):
        self.ip = None
        self.name = None
        self.available_keys = []

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self.ip = user_input["ip_address"]
            self.name = user_input["name"]
            session = async_get_clientsession(self.hass)
            url = DEFAULT_URL.format(ip=self.ip)

            try:
                async with async_timeout.timeout(5):
                    resp = await session.get(url)
                    resp.raise_for_status()
                    data = await resp.json()
                self.available_keys = flatten_keys(data["SBI"])
                return await self.async_step_select_keys()
            except Exception as e:
                _LOGGER.error(f"Cannot connect to {url}: {e}")
                return self.async_show_form(
                    step_id="user",
                    data_schema=vol.Schema({
                        vol.Required("ip_address"): str,
                        vol.Required("name"): str
                    }),
                    errors={"base": "cannot_connect"}
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("ip_address"): str,
                vol.Required("name"): str
            })
        )

    async def async_step_select_keys(self, user_input=None):
        if user_input is not None:
            selected_keys = [k for k, v in user_input.items() if v]
            return self.async_create_entry(
                title=self.name,
                data={
                    "ip_address": self.ip,
                    "name": self.name,
                    "selected_keys": selected_keys
                }
            )
        schema = vol.Schema({
            vol.Optional(key): bool for key in self.available_keys
        })
        return self.async_show_form(
            step_id="select_keys",
            data_schema=schema
        )

def flatten_keys(d, parent_key=""):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}.{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_keys(v, new_key))
        else:
            items.append(new_key)
    return items
