"""Basic configuration for the IPS demo."""

FORWARDING_RULES = {
    "http": 8080,
    "https": 8443,
}

EXCLUDED_IP_RANGES = [
    "192.168.53."
]
