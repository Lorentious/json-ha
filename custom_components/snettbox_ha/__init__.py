import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "json-ha"

async def async_setup(hass, config):
    """Erstes Setup beim Start von Home Assistant."""
    _LOGGER.info("Initialisiere Snettbox...")

    # Daten im hass.data-Container speichern
    hass.data[DOMAIN] = {
        "message": "Hallo von Snettbox!"
    }

    # Beispiel: Dienst registrieren
    async def handle_test_service(call):
        _LOGGER.info("Testdienst wurde aufgerufen")
        hass.bus.async_fire("my_component_test_event", {"message": "Hallo Welt!"})

    hass.services.async_register(DOMAIN, "say_hello", handle_test_service)

    return True
