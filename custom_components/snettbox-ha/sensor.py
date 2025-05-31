from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import TEMP_CELSIUS
from datetime import timedelta
import async_timeout
import logging

from .const import DOMAIN, DEFAULT_URL

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    ip = config_entry.data["IP-Address"]
    name = config_entry.data["Name"]
    update_interval = config_entry.data.get("Interval", 15)
    selected_groups = config_entry.data.get("selected_groups", [])

    session = async_get_clientsession(hass)
    url = DEFAULT_URL.format(ip=ip)

    async def async_update_data():
        try:
            async with async_timeout.timeout(5):
                response = await session.get(url)
                response.raise_for_status()
                return await response.json()
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="json_ha",
        update_method=async_update_data,
        update_interval=timedelta(seconds=update_interval),
    )

    await coordinator.async_config_entry_first_refresh()
    data = coordinator.data
    sbi = data.get("SBI", {})
    uid = sbi.get("UID", "unknown")
    version = sbi.get("Ver", "unknown")

    entities = []

    # UID, Ver, t, Sta, Err oben direkt integrieren
    for key in ["UID", "Ver", "t", "Sta", "Err"]:
        if key in sbi:
            entities.append(JsonHaSensor(hass, name, "SBI", key, ip, update_interval, uid, version, coordinator))

    # Untergruppen durchgehen (SB, GRID, etc.)
    for group in selected_groups:
        group_data = sbi.get(group, {})
        if isinstance(group_data, dict):
            for subkey, value in group_data.items():
                full_key = f"{group}.{subkey}"
                entities.append(JsonHaSensor(hass, name, group, full_key, ip, update_interval, uid, version, coordinator))
        else:
            _LOGGER.warning(f"{group} ist keine Untergruppe im JSON.")

    async_add_entities(entities)


class JsonHaSensor(Entity):
    def __init__(self, hass, name, group, key, ip, interval, uid, version, coordinator):
        self._hass = hass
        self._name = f"{name} {key}"
        self._group = group
        self._key = key
        self._ip = ip
        self._interval = interval
        self._uid = uid
        self._version = version
        self._state = None
        self._coordinator = coordinator

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return f"{self._uid}_{self._key}"

    @property
    def state(self):
        return self._state

    @property
    def available(self):
        return self._coordinator.last_update_success

    @property
    def extra_state_attributes(self):
        return {
            "uid": self._uid,
            "version": self._version,
            "group": self._group,
            "key": self._key,
            "ip": self._ip,
            "interval": self._interval,
        }

    async def async_update(self):
        await self._coordinator.async_request_refresh()
        self._update_from_data()

    async def async_added_to_hass(self):
        self._coordinator.async_add_listener(self._handle_coordinator_update)
        self._update_from_data()

    def _handle_coordinator_update(self):
        self._update_from_data()
        self.async_write_ha_state()

    def _update_from_data(self):
        data = self._coordinator.data or {}
        sbi = data.get("SBI", {})
        if self._group == "SBI":
            self._state = sbi.get(self._key)
        else:
            group_data = sbi.get(self._group, {})
            if isinstance(group_data, dict):
                self._state = group_data.get(self._key.split(".")[-1])
            else:
                self._state = None
