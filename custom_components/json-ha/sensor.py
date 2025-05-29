from homeassistant.helpers.entity import Entity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import logging
from .const import DOMAIN
from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)

def get_value_from_path(data, path):
    for part in path.split("."):
        data = data.get(part, {})
    return data if not isinstance(data, dict) else None

async def async_setup_entry(hass, entry, async_add_entities):
    ip = entry.data["ip_address"]
    name = entry.data["name"]
    update_interval = entry.data.get("update_interval", 60)
    selected_keys = entry.data["selected_keys"]

    entities = []
    for key in selected_keys:
        entities.append(JsonHaSensor(hass, name, key, ip, update_interval))

    async_add_entities(entities, True)

class JsonHaSensor(Entity):
    def __init__(self, hass, name, key, ip, update_interval):
        self._hass = hass
        self._name = f"{name} {key.replace('.', '_')}"
        self._key = key
        self._ip = ip
        self._state = None
        self._unsub_update = None
        self._update_interval = timedelta(seconds=update_interval)

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
        return False  # Kein automatisches Polling von HA

    async def async_added_to_hass(self):
        self._unsub_update = async_track_time_interval(
            self._hass, self.async_update, self._update_interval
        )
        await self.async_update()

    async def async_will_remove_from_hass(self):
        if self._unsub_update:
            self._unsub_update()
            self._unsub_update = None

    async def async_update(self, now=None):
        url = f"http://{self._ip}/"
        session = async_get_clientsession(self._hass)
        try:
            async with session.get(url, timeout=5) as resp:
                data = await resp.json()
            sbi = data.get("SBI", {})
            self._state = get_value_from_path(sbi, self._key)
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error(f"Fehler beim Abrufen der JSON-Daten: {e}")
            self._state = None
