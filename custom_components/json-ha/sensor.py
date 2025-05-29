from homeassistant.helpers.entity import Entity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import logging
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

def get_value_from_path(data, path):
    for part in path.split("."):
        data = data.get(part, {})
    return data if not isinstance(data, dict) else None

async def async_setup_entry(hass, entry, async_add_entities):
    ip = entry.data["ip_address"]
    name = entry.data["name"]
    selected_keys = entry.data["selected_keys"]

    entities = []
    for key in selected_keys:
        entities.append(JsonHaSensor(hass, name, key, ip))

    async_add_entities(entities, True)

class JsonHaSensor(Entity):
    def __init__(self, hass, prefix, key, ip):
        self._hass = hass
        self._key = key
        self._ip = ip
        self._name = f"{prefix} {key.replace('.', '_')}"
        self._state = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unique_id(self):
        return f"{self._ip}_{self._key}"

    @property
    def should_poll(self):
        return True  # Polling aktiviert

    async def async_update(self):
        """Hol Daten neu via HTTP."""
        url = f"http://{self._ip}/"
        session = async_get_clientsession(self._hass)
        try:
            async with session.get(url, timeout=5) as resp:
                data = await resp.json()
            sbi = data.get("SBI", {})
            self._state = get_value_from_path(sbi, self._key)
        except Exception as e:
            _LOGGER.error("Fehler beim Abrufen der JSON-Daten: %s", e)
            self._state = None
