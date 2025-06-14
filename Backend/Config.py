FORWARDING_RULES = {
    "http": 8080,
    "https": 8443,
}

EXCLUDED_IP_RANGES = [
    #"192.168.53."
]

# Ranges used by the fictive "Denamysch" network which should
# immediately be blocked when detected.
DENAMYSCH_IP_RANGES = [
    "203.0.113.",
    "198.51.100."
]

# Thresholds for various detection rules
PORT_SCAN_THRESHOLD = 10  # distinct ports within the time window
PORT_SCAN_WINDOW = 5      # seconds
BRUTE_FORCE_THRESHOLD = 5 # failed attempts within the time window
BRUTE_FORCE_WINDOW = 60   # seconds

SYN_FLOOD_PROTECTION_ENABLED = True
SYN_FLOOD_TIMEOUT = 2

TC_INTERFACE = "eth0"

# Maximum number of log records to keep when truncating log files
MAX_LOG_RECORDS = 1000
