from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry):
    ip = entry.data["ip_address"]
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "ip": ip,
        "groups": entry.data["selected_groups"],
        "interval": entry.data.get("interval", 30),
        "name": entry.data["name"]
    }

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass, entry):
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
