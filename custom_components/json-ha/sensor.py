from homeassistant.helpers.entity import Entity
import requests
import logging
from .const import DOMAIN, DEFAULT_URL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up JSON sensors."""
    ip = hass.data[DOMAIN][entry.entry_id]["ip"]
    url = DEFAULT_URL.format(ip=ip)

    try:
        response = requests.get(url, timeout=5)
        data = response.json()
    except Exception as e:
        _LOGGER.error("Fehler beim Abrufen von JSON: %s", e)
        data = {}

    entities = []
    for key, value in data.items():
        entities.append(JsonHaSensor(name=key, value=value, ip=ip))

    async_add_entities(entities, True)

class JsonHaSensor(Entity):
    def __init__(self, name, value, ip):
        self._name = f"snettbox_{name}"
        self._state = value
        self._ip = ip

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unique_id(self):
        return f"{self._ip}_{self._name}"
