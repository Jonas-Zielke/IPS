# main.py
import json
import time
import threading
from scapy.all import sniff, IP, TCP, UDP
from datetime import datetime
from Config import FORWARDING_RULES, EXCLUDED_IP_RANGES, SYN_FLOOD_PROTECTION_ENABLED
from Module import Rules, Block
from Module.ResourceManager import ResourceManager
import uvicorn
from Module.API.API import app
from Module.Manage_Connections import get_connection_manager
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
logfile = BASE_DIR / 'Logs/network_traffic_logs.json'
resource_logfile = BASE_DIR / 'Logs/resource_usage.json'
connections_logfile = BASE_DIR / 'Logs/active_connections.json'
rules = []

# Initialize connection manager lazily so threads only start when needed
connection_manager = get_connection_manager()

def initialize_json_files():
    files = [logfile, resource_logfile, connections_logfile]
    for file in files:
        if not file.exists():
            with open(file, 'w') as f:
                json.dump([], f)
                print(f"Initialized {file}")  # Debugging-Ausgabe

initialize_json_files()

def log_to_json(data, file):
    print(f"Writing data to {file}: {data}")  # Debugging-Ausgabe
    if not file.exists():
        with open(file, 'w') as f:
            json.dump([data], f)
    else:
        with open(file, 'r+') as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
            logs.append(data)
            f.seek(0)
            json.dump(logs, f, indent=4)
    print(f"Successfully wrote data to {file}")  # Debugging-Ausgabe

def register_rule(rule_func):
    global rules
    rules.append(rule_func)

def is_ip_excluded(ip):
    return any(ip.startswith(prefix) for prefix in EXCLUDED_IP_RANGES)

def packet_callback(packet):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "ip_src": None,
        "ip_dst": None,
        "proto": None,
        "sport": None,
        "dport": None,
        "payload": None,
        "http": False,
        "https": False
    }

    if IP in packet:
        log_entry["ip_src"] = packet[IP].src
        log_entry["ip_dst"] = packet[IP].dst

        if is_ip_excluded(log_entry["ip_src"]) or is_ip_excluded(log_entry["ip_dst"]):
            return

        if TCP in packet:
            log_entry["proto"] = "TCP"
            log_entry["sport"] = packet[TCP].sport
            log_entry["dport"] = packet[TCP].dport
            log_entry["payload"] = bytes(packet[TCP].payload).decode('utf-8', errors='ignore')
            if packet[TCP].dport == 80 or packet[TCP].sport == 80:
                log_entry["http"] = True
            elif packet[TCP].dport == 443 or packet[TCP].sport == 443:
                log_entry["https"] = True
        elif UDP in packet:
            log_entry["proto"] = "UDP"
            log_entry["sport"] = packet[UDP].sport
            log_entry["dport"] = packet[UDP].dport
            log_entry["payload"] = bytes(packet[UDP].payload).decode('utf-8', errors='ignore')

    if log_entry["proto"] in ["TCP", "UDP"]:
        log_to_json(log_entry, logfile)
        for rule in rules:
            rule(packet, log_entry)

def log_resource_usage():
    resource_usage = {
        "timestamp": datetime.now().isoformat(),
        "cpu_usage": ResourceManager.get_cpu_usage(),
        "ram_usage": ResourceManager.get_ram_usage(),
        "network_traffic": ResourceManager.get_network_traffic()
    }
    log_to_json(resource_usage, resource_logfile)

def log_connections():
    active_connections = connection_manager.connections
    connections_list = [
        {
            "src_ip": conn[0],
            "src_port": conn[1],
            "dst_ip": conn[2],
            "dst_port": conn[3],
            "timestamp": datetime.fromtimestamp(timestamp).isoformat()
        }
        for conn, timestamp in active_connections.items()
    ]
    with open(connections_logfile, 'w') as f:
        json.dump(connections_list, f, indent=4)
    print(f"Logged connections to {connections_logfile}")  # Debugging-Ausgabe

register_rule(Rules.log_http_traffic)
register_rule(Rules.log_https_traffic)
register_rule(Rules.forward_traffic)
register_rule(Rules.detect_denamysch_ip)
register_rule(Rules.detect_port_scan)
register_rule(Rules.detect_sql_injection)
register_rule(Rules.detect_xss)
register_rule(Rules.detect_directory_traversal)
register_rule(Rules.detect_bruteforce)
register_rule(Rules.detect_dns_amplification)
register_rule(Rules.detect_ntp_amplification)
register_rule(Rules.detect_suspicious_user_agent)
register_rule(Rules.detect_large_payload)

if SYN_FLOOD_PROTECTION_ENABLED:
    register_rule(Rules.monitor_tcp_connections)

# Beispielhafte Nutzung der Block-Funktionen
#Block.temp_block("192.168.1.1", 60, "Suspicious activity")
#Block.perma_block("192.168.1.2", "Repeated attacks")
#Block.traffic_slowdown("192.168.1.3", 1, "Bandwidth abuse")

# Protokollieren der Ressourcennutzung und Verbindungen alle 10 Sekunden
def start_resource_logging():
    while True:
        log_resource_usage()
        log_connections()
        time.sleep(10)

def start_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)

resource_logging_thread = threading.Thread(target=start_resource_logging, daemon=True)
resource_api_thread = threading.Thread(target=start_api, daemon=True)
resource_api_thread.start()
resource_logging_thread.start()

sniff(prn=packet_callback, store=0)
