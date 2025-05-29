async def async_setup_entry(hass, entry):
    """Wird aufgerufen, wenn eine Config-Entry geladen wird."""
    _LOGGER.debug("Setze Entry Setup auf für: %s", entry.data)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry.data

    return True
async def async_unload_entry(hass, entry):
    """Wird aufgerufen, wenn die Integration entfernt wird."""
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
