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
        self.update_interval = 60
        self.available_groups = []

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self.ip = user_input["ip_address"]
            self.name = user_input["name"]
            self.update_interval = user_input.get("update_interval", 60)
            session = async_get_clientsession(self.hass)
            url = DEFAULT_URL.format(ip=self.ip)

            try:
                async with async_timeout.timeout(5):
                    resp = await session.get(url)
                    resp.raise_for_status()
                    data = await resp.json()
                sbi = data.get("SBI", {})
                self.available_groups = []
                for key, val in sbi.items():
                    if isinstance(val, dict):
                        self.available_groups.append(key)
                    else:
                        self.available_groups.append("SBI_ROOT")
                        break  # Nur einmal hinzufügen
                return await self.async_step_select_groups()
            except Exception as e:
                _LOGGER.error(f"Cannot connect to {url}: {e}")
                return self.async_show_form(
                    step_id="user",
                    data_schema=vol.Schema({
                        vol.Required("ip_address"): str,
                        vol.Required("name"): str,
                        vol.Required("update_interval", default=60): int,
                    }),
                    errors={"base": "cannot_connect"}
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("ip_address"): str,
                vol.Required("name"): str,
                vol.Required("update_interval", default=60): int,
            })
        )

    async def async_step_select_groups(self, user_input=None):
        if user_input is not None:
            selected_groups = [grp for grp, val in user_input.items() if val]
            return self.async_create_entry(
                title=self.name,
                data={
                    "ip_address": self.ip,
                    "name": self.name,
                    "update_interval": self.update_interval,
                    "selected_groups": selected_groups,
                }
            )

        schema = vol.Schema({
            vol.Optional(group): bool for group in self.available_groups
        })
        return self.async_show_form(
            step_id="select_groups",
            data_schema=schema,
        )
