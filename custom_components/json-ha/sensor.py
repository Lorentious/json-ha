from homeassistant.helpers.entity import Entity
import requests
import logging
from .const import DOMAIN
from .const import DEFAULT_URL

_LOGGER = logging.getLogger(__name__)

def get_value_from_path(data, path):
    for part in path.split("."):
        data = data.get(part, {})
    return data if not isinstance(data, dict) else None

async def async_setup_entry(hass, entry, async_add_entities):
    ip = entry.data["ip_address"]
    name = entry.data["name"]
    selected_keys = entry.data["selected_keys"]

    try:
        response = requests.get(f"http://{ip}/", timeout=5)
        data = response.json()["SBI"]
    except Exception as e:
        _LOGGER.error("Fehler beim Abrufen der JSON-Daten: %s", e)
        return

    entities = []
    for key in selected_keys:
        value = get_value_from_path(data, key)
        entities.append(JsonHaSensor(name, key, value, ip))

    async_add_entities(entities, True)

class JsonHaSensor(Entity):
    def __init__(self, prefix, key, value, ip):
        self._key = key
        self._state = value
        self._ip = ip
        self._name = f"{prefix} {key.replace('.', '_')}"

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
        return False
