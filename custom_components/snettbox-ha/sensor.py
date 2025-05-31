from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, DEVICE_CATEGORIES, ICONS
from homeassistant.helpers.entity import DeviceInfo

def flatten_json(data, parent_key=''):
    """Flacht geschachtelte JSON in Schlüssel-Werte-Paare ab."""
    items = []
    for k, v in data.items():
        new_key = f"{parent_key}.{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_json(v, new_key))
        else:
            items.append((new_key, v))
    return items

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    selected_groups = entry.data.get("selected_groups", [])
    ip = entry.data["IP-Address"]
    name = entry.data["Name"]

    # UID und VER immer hinzufügen
    raw_data = coordinator.data.get("SBI", {})
    static_keys = {k: v for k, v in raw_data.items() if not isinstance(v, dict)}
    dynamic_data = {k: v for k, v in raw_data.items() if isinstance(v, dict) and k in selected_groups}

    entities = []

    # UID, VER, t, Sta, Err etc. als Entitäten
    for key, value in static_keys.items():
        unique_id = f"{ip}_{key}"
        icon = ICONS.get(key, "mdi:information-outline")
        entities.append(JsonHaSensor(coordinator, name, key, value, unique_id, key, icon, "diagnose"))

    # Alle ausgewählten Gruppen auflösen
    for group_name, group_data in dynamic_data.items():
        category = DEVICE_CATEGORIES.get(group_name, "sensor")
        for key, value in group_data.items():
            entity_key = f"{group_name}.{key}"
            unique_id = f"{ip}_{entity_key}"
            icon = ICONS.get(key, "mdi:information-outline")
            entities.append(JsonHaSensor(coordinator, name, entity_key, value, unique_id, group_name, icon, category))

    async_add_entities(entities)

class JsonHaSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, name, key, value, unique_id, group, icon, category):
        super().__init__(coordinator)
        self._attr_name = f"{name} {key}"
        self._attr_unique_id = unique_id
        self._attr_native_value = value
        self._group = group
        self._icon = icon
        self._category = category

    @property
    def icon(self):
        return self._icon

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self.coordinator.data['SBI'].get('UID', 'unknown')}")},
            name=self.coordinator.data['SBI'].get("UID", "JSON Device"),
            manufacturer="json-ha",
            model=self.coordinator.data['SBI'].get("Ver", "unknown"),
        )

    @property
    def entity_category(self):
        if self._category == "diagnose":
            return "diagnostic"
        elif self._category == "steuerung":
            return "config"
        else:
            return None

    @property
    def native_value(self):
        # Jedes Mal den neuesten Wert aus dem Coordinator holen
        try:
            keys = self._attr_name.split(" ")[1].split(".")
            value = self.coordinator.data["SBI"]
            for k in keys:
                value = value[k]
            return value
        except Exception:
            return None
