import json
from scapy.all import sniff, IP, TCP, UDP
from datetime import datetime

def log_http_traffic(packet):
    if packet["http"]:
        print(f"HTTP traffic detected: {packet}")


def log_https_traffic(packet):
    if packet["https"]:
        print(f"HTTPS traffic detected: {packet}")