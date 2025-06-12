"""Packet processing rules used by the IPS."""

from scapy.all import IP, TCP, UDP, send
from Config import FORWARDING_RULES


def log_http_traffic(packet) -> None:
    """Print a message when HTTP traffic is detected."""

    if packet["http"]:
        print(f"HTTP traffic detected: {packet}")


def log_https_traffic(packet) -> None:
    """Print a message when HTTPS traffic is detected."""

    if packet["https"]:
        print(f"HTTPS traffic detected: {packet}")


def forward_traffic(packet) -> None:
    """Forward HTTP/HTTPS traffic to a configured port."""

    if packet["http"]:
        new_port = FORWARDING_RULES.get("http")
    elif packet["https"]:
        new_port = FORWARDING_RULES.get("https")
    else:
        new_port = None

    if new_port:
        # Erstelle ein neues Paket mit dem neuen Zielport
        ip_layer = IP(src=packet["ip_src"], dst=packet["ip_dst"])
        if packet["proto"] == "TCP":
            transport_layer = TCP(sport=packet["sport"], dport=new_port, flags='S')
        elif packet["proto"] == "UDP":
            transport_layer = UDP(sport=packet["sport"], dport=new_port)

        new_packet = ip_layer / transport_layer / packet["payload"]

        # Sende das neue Paket
        send(new_packet)
        print(f"Forwarded traffic: {packet} to port {new_port}")
