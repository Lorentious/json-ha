from homeassistant.helpers.entity import Entity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta
from .const import DOMAIN
import logging
import json
import os

_LOGGER = logging.getLogger(__name__)

# Icons laden
ICON_PATH = os.path.join(os.path.dirname(__file__), "icons.json")
try:
    with open(ICON_PATH, "r", encoding="utf-8") as f:
        ICON_MAP = json.load(f)
except Exception as e:
    _LOGGER.warning(f"Konnte icons.json nicht laden: {e}")
    ICON_MAP = {}

def flatten_keys(d, parent_key=""):
    """Rekursiv alle Keys aus dict holen, mit Punkt-Notation"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}.{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_keys(v, new_key))
        else:
            items.append(new_key)
    return items

def get_value_from_path(data, path):
    """Hole Wert anhand Pfad mit Punkt-Notation"""
    for part in path.split("."):
        data = data.get(part, {})
    return data if not isinstance(data, dict) else None

async def async_setup_entry(hass, entry, async_add_entities):
    ip = entry.data["IP-Address"]
    name = entry.data["Name"]
    update_interval = entry.data.get("Interval", 15)
    selected_groups = entry.data["selected_groups"]

    entities = []
    session = async_get_clientsession(hass)

    url = f"http://{ip}/"
    try:
        async with session.get(url, timeout=5) as resp:
            data = await resp.json()

        sbi = data.get("SBI", {})
        uid = sbi.get("UID", "unknown")
        version = sbi.get("Ver", "unknown")

        # Alle Schlüssel auf oberster Ebene von SBI, die KEIN dict sind
        top_level_keys = {k: v for k, v in sbi.items() if not isinstance(v, dict)}
        for key in top_level_keys:
            entities.append(JsonHaSensor(hass, name, name, key, ip, update_interval, uid, version))

        # Sensoren für verschachtelte Gruppen wie SB, GRID, INV
        for group in selected_groups:
            group_data = sbi.get(group, {})
            keys = flatten_keys(group_data, group)
            for key in keys:
                entities.append(JsonHaSensor(hass, name, group, key, ip, update_interval, uid, version))

    except Exception as e:
        _LOGGER.error(f"Fehler beim Abrufen der JSON-Daten: {e}")

    async_add_entities(entities, True)


class JsonHaSensor(Entity):
    def __init__(self, hass, base_name, group, key, ip, update_interval, uid, version):
        self._hass = hass
        self._base_name = base_name
        self._group = group
        self._key = key
        self._ip = ip
        self._uid = uid
        self._version = version
        self._state = None
        self._unsub_update = None
        self._update_interval = timedelta(seconds=update_interval)

        key_short = key[len(group) + 1:] if key.startswith(group + ".") else key
        self._name = f"{base_name} {key_short}"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unique_id(self):
        return f"{self._ip}_{self._group}_{self._key}"

    @property
    def should_poll(self):
        return False

    @property
    def icon(self):
        return ICON_MAP.get(self._key)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._uid)},
            "name": self._base_name,
            "manufacturer": "Manu",
            "model": "Box",
            "sw_version": self._version,
        }

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
