# main.py
import json
from scapy.all import sniff, IP, TCP, UDP
from datetime import datetime
from Config import FORWARDING_RULES, EXCLUDED_IP_RANGES
from Module import Rules, Block

logfile = 'Logs/network_traffic_logs.json'
rules = []

def log_to_json(data):
    with open(logfile, 'a') as f:
        json.dump(data, f)
        f.write('\n')

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
        log_to_json(log_entry)
        for rule in rules:
            rule(log_entry)

register_rule(Rules.log_http_traffic)
register_rule(Rules.log_https_traffic)
register_rule(Rules.forward_traffic)


Block.temp_block("192.168.1.1", 60, "Suspicious activity")
Block.perma_block("192.168.1.2", "Repeated attacks")
Block.traffic_slowdown("192.168.1.3", 1, "Bandwidth abuse")

sniff(prn=packet_callback, store=0)
