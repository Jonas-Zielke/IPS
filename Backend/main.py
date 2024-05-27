import json
from scapy.all import sniff, IP, TCP, UDP
from datetime import datetime
#from Config import Config
from Module import Rules

logfile = 'Logs/network_traffic_logs.json'
rules = []


# Funktion zum Schreiben von Daten in eine JSON-Datei
def log_to_json(data):
    with open(logfile, 'a') as f:
        json.dump(data, f)
        f.write('\n')


# Funktion zur Registrierung von Regelprüfungsfunktionen
def register_rule(rule_func):
    global rules
    rules.append(rule_func)


# Callback-Funktion zur Verarbeitung jedes Pakets
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





# Regeln registrieren
register_rule(Rules.log_http_traffic)
register_rule(Rules.log_https_traffic)

# Start sniffing
sniff(prn=packet_callback, store=0)
