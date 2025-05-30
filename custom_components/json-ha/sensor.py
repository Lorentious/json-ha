from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_NAME
import requests
import logging

_LOGGER = logging.getLogger(__name__)

def flatten_json(y, parent_key='', sep='_'):
    items = {}
    for k, v in y.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_json(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items

def setup_platform(hass, config, add_entities, discovery_info=None):
    url = config.get("url")
    name = config.get(CONF_NAME, "JSON Sensor")

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        json_data = response.json()
    except Exception as e:
        _LOGGER.error(f"Failed to fetch data from {url}: {e}")
        return

    # Daten flach machen
    flat = flatten_json(json_data)

    sensors = []
    for key, value in flat.items():
        sensors.append(JsonSensor(name, key, value, url))

    add_entities(sensors, True)


class JsonSensor(Entity):
    def __init__(self, base_name, key, value, url):
        self._name = f"{base_name} {key}"
        self._state = value
        self._key = key
        self._url = url

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    def update(self):
        try:
            response = requests.get(self._url, timeout=5)
            response.raise_for_status()
            json_data = response.json()
            flat = flatten_json(json_data)
            self._state = flat.get(self._key)
        except Exception as e:
            _LOGGER.error(f"Failed to update data from {self._url}: {e}")
