DOMAIN = "snettbox-ha"
DEFAULT_URL = "http://{ip}/data.json"

# Optional: Icons pro Schlüssel
ICONS = {
    "T": "mdi:thermometer",
    "U": "mdi:flash",
    "I": "mdi:current-dc",
    "SoC": "mdi:battery",
    "SoH": "mdi:heart-pulse",
    "Pg": "mdi:transmission-tower",
    "Pac": "mdi:solar-power",
}

# Optional: Gruppierung in Kategorien
DEVICE_CATEGORIES = {
    "SB": "sensor",
    "GRID": "sensor",
    "INV": "sensor",
    "SYS": "diagnose",
}
