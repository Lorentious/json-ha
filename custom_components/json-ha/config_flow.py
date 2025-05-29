from homeassistant import config_entries
import voluptuous as vol
import requests
from .const import DOMAIN, DEFAULT_URL

class JsonHaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    def __init__(self):
        self.ip = None
        self.name = None
        self.available_groups = []

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self.ip = user_input["ip_address"]
            self.name = user_input["name"]
            interval = user_input.get("interval", 30)

            try:
                url = DEFAULT_URL.format(ip=self.ip)
                resp = requests.get(url, timeout=5)
                data = resp.json()
                self.available_groups = list(data["SBI"].keys())
                self.interval = interval

                return await self.async_step_select_groups()
            except Exception:
                return self.async_show_form(
                    step_id="user",
                    data_schema=vol.Schema({
                        vol.Required("ip_address"): str,
                        vol.Required("name"): str,
                        vol.Required("interval", default=30): int
                    }),
                    errors={"base": "cannot_connect"}
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("ip_address"): str,
                vol.Required("name"): str,
                vol.Required("interval", default=30): int
            })
        )

    async def async_step_select_groups(self, user_input=None):
        if user_input is not None:
            selected = [g for g, v in user_input.items() if v]
            return self.async_create_entry(
                title=self.name,
                data={
                    "ip_address": self.ip,
                    "name": self.name,
                    "selected_groups": selected,
                    "interval": self.interval
                }
            )

        schema = vol.Schema({
            vol.Optional(group): True for group in self.available_groups
        })

        return self.async_show_form(
            step_id="select_groups",
            data_schema=schema
        )
