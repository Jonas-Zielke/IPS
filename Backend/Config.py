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

# Log rotation configuration
# Maximum number of records to keep per log file
LOG_MAX_RECORDS = 1000
# Remove log entries older than this many days (None disables age based cleanup)
LOG_MAX_AGE_DAYS = 30
