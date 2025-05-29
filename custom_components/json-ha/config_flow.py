from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, DEFAULT_URL
import async_timeout
import aiohttp

class JsonHaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self.ip = user_input["ip_address"]
            self.name = user_input["name"]

            url = DEFAULT_URL.format(ip=self.ip)

            try:
                async with async_timeout.timeout(5):
                    session = aiohttp.ClientSession()
                    async with session.get(url) as resp:
                        data = await resp.json()
                    await session.close()

                self.available_keys = flatten_keys(data["SBI"])
                return await self.async_step_select_keys()
            except Exception:
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
