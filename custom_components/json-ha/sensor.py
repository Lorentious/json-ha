from homeassistant.helpers.entity import Entity
import requests
import logging
from .const import DOMAIN, DEFAULT_URL
from datetime import timedelta
import asyncio

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    ip = entry.data["ip_address"]
    name = entry.data["name"]
    groups = entry.data["selected_groups"]
    interval = entry.data.get("interval", 30)

    url = DEFAULT_URL.format(ip=ip)
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()["SBI"]
    except Exception as e:
        _LOGGER.error("Fehler beim Abrufen der JSON-Daten: %s", e)
        return

    entities = []
    for group in groups:
        group_data = data.get(group, {})
        for key, value in group_data.items():
            entities.append(JsonHaSensor(name, ip, group, key, interval))

    async_add_entities(entities, True)

class JsonHaSensor(Entity):
    def __init__(self, name, ip, group, key, interval):
        self._name = f"{name} {group}.{key}"
        self._ip = ip
        self._group = group
        self._key = key
        self._state = None
        self._interval = interval
        self._attr_unique_id = f"{ip}_{group}_{key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, ip)},
            "name": name,
            "manufacturer": "Snettbox",
            "model": "JSON Device"
        }

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def should_poll(self):
        return True

    async def async_update(self):
        await asyncio.sleep(0)
        try:
            url = DEFAULT_URL.format(ip=self._ip)
            resp = requests.get(url, timeout=5)
            data = resp.json()["SBI"]
            self._state = data.get(self._group, {}).get(self._key)
        except Exception as e:
            _LOGGER.warning("Update fehlgeschlagen: %s", e)
            self._state = None
