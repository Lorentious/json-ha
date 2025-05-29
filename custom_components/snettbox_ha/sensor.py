from homeassistant.helpers.entity import Entity

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async_add_entities([MySensor()])

class MySensor(Entity):
    def __init__(self):
        self._state = "Hello"

    @property
    def name(self):
        return "My Sensor"

    @property
    def state(self):
        return self._state
