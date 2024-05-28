import json
from scapy.all import sniff, IP, TCP, UDP, send
from datetime import datetime
from Config import FORWARDING_RULES
from Module.Manage_Connections import connection_manager


def log_http_traffic(packet):
    if packet["http"]:
        print(f"HTTP traffic detected: {packet}")


def log_https_traffic(packet):
    if packet["https"]:
        print(f"HTTPS traffic detected: {packet}")


def forward_traffic(packet):
    if packet["http"]:
        new_port = FORWARDING_RULES.get("http")
    elif packet["https"]:
        new_port = FORWARDING_RULES.get("https")
    else:
        new_port = None

    if new_port:
        ip_layer = IP(src=packet["ip_src"], dst=packet["ip_dst"])
        if packet["proto"] == "TCP":
            transport_layer = TCP(sport=packet["sport"], dport=new_port, flags='S')
        elif packet["proto"] == "UDP":
            transport_layer = UDP(sport=packet["sport"], dport=new_port)

        new_packet = ip_layer / transport_layer / packet["payload"]
        send(new_packet)
        print(f"Forwarded traffic: {packet} to port {new_port}")


def monitor_tcp_connections(packet):
    if TCP in packet:
        if packet[TCP].flags == 'S':  # SYN-Flag
            connection_manager.add_connection(packet[IP].src, packet[TCP].sport, packet[IP].dst, packet[TCP].dport)
        elif packet[TCP].flags == 'SA' or packet[TCP].flags == 'A':  # SYN-ACK or ACK-Flag
            connection_manager.remove_connection(packet[IP].src, packet[TCP].sport, packet[IP].dst, packet[TCP].dport)
