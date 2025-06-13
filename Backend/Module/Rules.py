import json
from datetime import datetime, timedelta
import logging
from scapy.all import sniff, IP, TCP, UDP, send

from Config import (
    FORWARDING_RULES,
    DENAMYSCH_IP_RANGES,
    PORT_SCAN_THRESHOLD,
    PORT_SCAN_WINDOW,
    BRUTE_FORCE_THRESHOLD,
    BRUTE_FORCE_WINDOW,
)
from Module.Manage_Connections import get_connection_manager

logger = logging.getLogger(__name__)

# Lazily initialize the connection manager when the rules module is imported
connection_manager = get_connection_manager()
from Module import Block


def log_http_traffic(pkt, entry):
    """Simple logger for HTTP traffic"""
    if entry.get("http"):
        logger.info("HTTP traffic detected: %s", entry)


def log_https_traffic(pkt, entry):
    if entry.get("https"):
        logger.info("HTTPS traffic detected: %s", entry)


def forward_traffic(pkt, entry):
    if entry.get("http"):
        new_port = FORWARDING_RULES.get("http")
    elif entry.get("https"):
        new_port = FORWARDING_RULES.get("https")
    else:
        new_port = None

    if new_port:
        ip_layer = IP(src=entry["ip_src"], dst=entry["ip_dst"])
        if entry["proto"] == "TCP":
            transport_layer = TCP(sport=entry["sport"], dport=new_port, flags='S')
        elif entry["proto"] == "UDP":
            transport_layer = UDP(sport=entry["sport"], dport=new_port)

        new_packet = ip_layer / transport_layer / entry["payload"]
        send(new_packet)
        logger.info("Forwarded traffic: %s to port %s", entry, new_port)


def monitor_tcp_connections(pkt, entry):
    """Track TCP handshakes to mitigate SYN flood attacks."""
    if TCP in pkt:
        if pkt[TCP].flags == 'S':  # SYN flag
            connection_manager.add_connection(pkt[IP].src, pkt[TCP].sport, pkt[IP].dst, pkt[TCP].dport)
        elif pkt[TCP].flags in ('SA', 'A'):  # SYN-ACK or ACK
            connection_manager.remove_connection(pkt[IP].src, pkt[TCP].sport, pkt[IP].dst, pkt[TCP].dport)


# ------------------------- Additional Detection Rules ------------------------

# Tracking dictionaries for stateful detections
_port_scan_history = {}
_brute_force_history = {}


def detect_denamysch_ip(pkt, entry):
    """Block traffic coming from known Denamysch ranges."""
    ip = entry.get("ip_src")
    if not ip:
        return
    if any(ip.startswith(prefix) for prefix in DENAMYSCH_IP_RANGES):
        Block.perma_block(ip, "Denamysch range")


def detect_port_scan(pkt, entry):
    ip = entry.get("ip_src")
    port = entry.get("dport")
    if not ip or port is None:
        return
    records = _port_scan_history.setdefault(ip, [])
    records.append((port, datetime.now()))
    cutoff = datetime.now() - timedelta(seconds=PORT_SCAN_WINDOW)
    _port_scan_history[ip] = [(p, ts) for p, ts in records if ts > cutoff]
    unique_ports = {p for p, _ in _port_scan_history.get(ip, [])}
    if len(unique_ports) >= PORT_SCAN_THRESHOLD:
        Block.temp_block(ip, 30, "Port scan detected")
        _port_scan_history.pop(ip, None)


def detect_sql_injection(pkt, entry):
    payload = entry.get("payload", "").lower()
    patterns = ["select", "union", " or ", "--", "' or", "drop table"]
    if any(p in payload for p in patterns):
        Block.temp_block(entry.get("ip_src"), 30, "SQL injection attempt")


def detect_xss(pkt, entry):
    payload = entry.get("payload", "").lower()
    if "<script" in payload or "javascript:" in payload:
        Block.temp_block(entry.get("ip_src"), 30, "XSS attempt")


def detect_directory_traversal(pkt, entry):
    payload = entry.get("payload", "")
    if "../" in payload:
        Block.temp_block(entry.get("ip_src"), 30, "Directory traversal attempt")


def detect_bruteforce(pkt, entry):
    ip = entry.get("ip_src")
    payload = entry.get("payload", "")
    if not ip or "POST /login" not in payload:
        return
    attempts = _brute_force_history.setdefault(ip, [])
    attempts.append(datetime.now())
    cutoff = datetime.now() - timedelta(seconds=BRUTE_FORCE_WINDOW)
    _brute_force_history[ip] = [ts for ts in attempts if ts > cutoff]
    if len(_brute_force_history.get(ip, [])) >= BRUTE_FORCE_THRESHOLD:
        Block.temp_block(ip, 30, "Brute force login")
        _brute_force_history.pop(ip, None)


def detect_dns_amplification(pkt, entry):
    if entry.get("proto") == "UDP" and entry.get("sport") == 53:
        if len(entry.get("payload", b"")) > 512:
            Block.temp_block(entry.get("ip_src"), 30, "DNS amplification")


def detect_ntp_amplification(pkt, entry):
    if entry.get("proto") == "UDP" and entry.get("sport") == 123:
        if len(entry.get("payload", b"")) > 468:
            Block.temp_block(entry.get("ip_src"), 30, "NTP amplification")


def detect_suspicious_user_agent(pkt, entry):
    payload = entry.get("payload", "").lower()
    if "user-agent" in payload:
        if any(tool in payload for tool in ["nmap", "sqlmap", "dirbuster"]):
            Block.temp_block(entry.get("ip_src"), 30, "Suspicious user agent")


def detect_large_payload(pkt, entry):
    if len(entry.get("payload", b"")) > 2000:
        Block.temp_block(entry.get("ip_src"), 30, "Large payload")
