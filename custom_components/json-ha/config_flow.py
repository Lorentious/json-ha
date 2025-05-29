from homeassistant import config_entries
import voluptuous as vol
import requests
from .const import DOMAIN

class JsonHaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for json_ha."""

    def __init__(self):
        self.ip = None
        self.name = None
        self.available_keys = []

    async def async_step_user(self, user_input=None):
        """Schritt 1: IP und Anzeigename"""
        if user_input is not None:
            self.ip = user_input["ip_address"]
            self.name = user_input["name"]

            # Versuche JSON zu laden
            try:
                url = f"http://{self.ip}/status.json"
                resp = requests.get(url, timeout=5)
                data = resp.json()

                # Flache Keyliste aus JSON generieren
                self.available_keys = flatten_keys(data["SBI"])
                return await self.async_step_select_keys()
            except Exception as e:
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
        """Schritt 2: Sensoren auswählen"""
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
            vol.Optional(key): True for key in self.available_keys
        })

        return self.async_show_form(
            step_id="select_keys",
            data_schema=schema
        )

def flatten_keys(d, parent_key=""):
    """Hilfsfunktion: wandelt verschachteltes dict in dot-notated keys um"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}.{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_keys(v, new_key))
        else:
            items.append(new_key)
    return items
