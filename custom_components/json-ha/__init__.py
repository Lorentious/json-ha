from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    """Wird nicht verwendet (wir nutzen config entries)."""
    return True

async def async_setup_entry(hass, entry):
    """Setup bei UI-Konfiguration."""
    _LOGGER.info("Starte mit IP: %s", entry.data["ip_address"])

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry.data

    # Hier kannst du z. B. eine Verbindung aufbauen oder eine Plattform starten
    return True

async def async_unload_entry(hass, entry):
    """Wird aufgerufen, wenn die Integration entfernt wird."""
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
