from homeassistant.helpers.entity import Entity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo
import logging
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    ip = entry.data["ip_address"]
    name = entry.data["name"]
    groups = entry.data["groups"]
    interval = entry.data.get("update_interval", 60)

    session = async_get_clientsession(hass)
    try:
        async with session.get(f"http://{ip}/", timeout=5) as resp:
            data = await resp.json()
        sbi = data.get("SBI", {})
    except Exception as e:
        _LOGGER.error("Fehler beim Abrufen der JSON-Daten: %s", e)
        return

    entities = []
    for group in groups:
        if group not in sbi:
            continue
        for key, value in sbi[group].items():
            full_key = f"{group}.{key}"
            entities.append(JsonHaSensor(hass, name, full_key, ip, interval))

    async_add_entities(entities, True)

class JsonHaSensor(Entity):
    def __init__(self, hass, prefix, key, ip, interval):
        self._hass = hass
        self._key = key
        self._ip = ip
        self._name = f"{prefix} {key.replace('.', '_')}"
        self._state = None
        self._interval = interval
        self._device_info = DeviceInfo(
            identifiers={(DOMAIN, ip)},
            name=prefix,
            manufacturer="Snettbox",
            model="JSON-HA",
            configuration_url=f"http://{ip}/",
        )

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
        return True

    @property
    def device_info(self):
        return self._device_info

    async def async_update(self):
        url = f"http://{self._ip}/"
        session = async_get_clientsession(self._hass)
        try:
            async with session.get(url, timeout=5) as resp:
                data = await resp.json()
            sbi = data.get("SBI", {})
            group, field = self._key.split(".")
            self._state = sbi.get(group, {}).get(field)
        except Exception as e:
            _LOGGER.error("Fehler beim Abrufen von %s: %s", self._key, e)
            self._state = None
