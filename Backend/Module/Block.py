import json
import os
import subprocess
from datetime import datetime, timedelta
import sys
import platform
import logging
import inspect

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logger = logging.getLogger(__name__)

from Config import EXCLUDED_IP_RANGES, TC_INTERFACE

block_log_file = 'Logs/block_log.json'
active_measures_file = 'Logs/active_measures.json'

def initialize_json_files():
    """Create log files if they don't already exist."""
    for file in (block_log_file, active_measures_file):
        if not os.path.exists(file):
            with open(file, 'w') as f:
                json.dump([], f)

def write_to_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

def read_from_json(file):
    with open(file, 'r') as f:
        return json.load(f)

def log_measure(measure):
    logs = read_from_json(block_log_file)
    logs.append(measure)
    from Config import MAX_LOG_RECORDS
    if len(logs) > MAX_LOG_RECORDS:
        logs = logs[-MAX_LOG_RECORDS:]
    write_to_json(block_log_file, logs)

def update_active_measures(measure):
    active_measures = read_from_json(active_measures_file)
    active_measures.append(measure)
    write_to_json(active_measures_file, active_measures)

def is_ip_excluded(ip):
    return any(ip.startswith(prefix) for prefix in EXCLUDED_IP_RANGES)

def add_iptables_rule(ip):
    try:
        subprocess.run(['sudo', 'iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'], check=True)
        logger.info("IP %s blocked.", ip)
    except subprocess.CalledProcessError as e:
        logger.error("Error blocking IP %s: %s", ip, e)

def remove_iptables_rule(ip):
    try:
        subprocess.run(['sudo', 'iptables', '-D', 'INPUT', '-s', ip, '-j', 'DROP'], check=True)
        logger.info("IP %s unblocked.", ip)
    except subprocess.CalledProcessError as e:
        logger.error("Error unblocking IP %s: %s", ip, e)

def add_windows_firewall_rule(ip):
    try:
        subprocess.run(['netsh', 'advfirewall', 'firewall', 'add', 'rule', f'name=Block {ip}', 'dir=in', 'action=block', f'remoteip={ip}'], check=True)
        logger.info("IP %s blocked.", ip)
    except subprocess.CalledProcessError as e:
        logger.error("Error blocking IP %s: %s", ip, e)

def remove_windows_firewall_rule(ip):
    try:
        subprocess.run(['netsh', 'advfirewall', 'firewall', 'delete', 'rule', f'name=Block {ip}'], check=True)
        logger.info("IP %s unblocked.", ip)
    except subprocess.CalledProcessError as e:
        logger.error("Error unblocking IP %s: %s", ip, e)

def add_tc_rule(ip, max_mb_per_sec, interface=TC_INTERFACE):
    """Limit traffic to and from an IP using tc on Linux."""
    rate = f"{max_mb_per_sec}mbit"
    try:
        # Ensure an ingress qdisc exists. This may fail if it already exists.
        subprocess.run(['sudo', 'tc', 'qdisc', 'add', 'dev', interface,
                        'handle', 'ffff:', 'ingress'], check=False)
        # Limit incoming traffic from the IP
        subprocess.run([
            'sudo', 'tc', 'filter', 'add', 'dev', interface, 'parent', 'ffff:',
            'protocol', 'ip', 'u32', 'match', 'ip', 'src', ip, 'police',
            'rate', rate, 'burst', '10k', 'drop', 'flowid', ':1'
        ], check=True)
        # Limit outgoing traffic to the IP
        subprocess.run([
            'sudo', 'tc', 'filter', 'add', 'dev', interface, 'parent', 'ffff:',
            'protocol', 'ip', 'u32', 'match', 'ip', 'dst', ip, 'police',
            'rate', rate, 'burst', '10k', 'drop', 'flowid', ':1'
        ], check=True)
        logger.info(
            "Traffic shaping applied for %s on %s at %s.",
            ip,
            interface,
            rate,
        )
    except subprocess.CalledProcessError as e:
        logger.error("Error applying tc rule for %s: %s", ip, e)

def remove_tc_rule(ip, interface=TC_INTERFACE):
    """Remove traffic shaping rules for an IP."""
    try:
        subprocess.run([
            'sudo', 'tc', 'filter', 'del', 'dev', interface, 'parent', 'ffff:',
            'protocol', 'ip', 'u32', 'match', 'ip', 'src', ip,
            'flowid', ':1'
        ], check=False)
        subprocess.run([
            'sudo', 'tc', 'filter', 'del', 'dev', interface, 'parent', 'ffff:',
            'protocol', 'ip', 'u32', 'match', 'ip', 'dst', ip,
            'flowid', ':1'
        ], check=False)
        logger.info("Traffic shaping removed for %s on %s.", ip, interface)
    except subprocess.CalledProcessError as e:
        logger.error("Error removing tc rule for %s: %s", ip, e)

def temp_block(ip, duration_minutes, reason=None):
    if is_ip_excluded(ip):
        return
    end_time = datetime.now() + timedelta(minutes=duration_minutes)
    measure = {
        "ip": ip,
        "measure": "temp_block",
        "start_time": datetime.now().isoformat(),
        "end_time": end_time.isoformat(),
        "reason": reason
    }
    if platform.system() == "Linux":
        add_iptables_rule(ip)
    elif platform.system() == "Windows":
        add_windows_firewall_rule(ip)
    log_measure(measure)
    update_active_measures(measure)
    logger.info("Temporary block set for IP %s for %s minutes.", ip, duration_minutes)

def perma_block(ip, reason=None):
    if is_ip_excluded(ip):
        return
    measure = {
        "ip": ip,
        "measure": "perma_block",
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "reason": reason
    }
    if platform.system() == "Linux":
        add_iptables_rule(ip)
    elif platform.system() == "Windows":
        add_windows_firewall_rule(ip)
    log_measure(measure)
    update_active_measures(measure)
    logger.info("Permanent block set for IP %s.", ip)

def traffic_slowdown(ip, max_mb_per_sec, reason=None):
    if is_ip_excluded(ip):
        return

    measure = {
        "ip": ip,
        "measure": "traffic_slowdown",
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "max_mb_per_sec": max_mb_per_sec,
        "reason": reason
    }
    should_apply = platform.system() == "Linux" and (
        os.getenv("TC_RULES_ENABLED") == "1" or not inspect.isfunction(platform.system)
    )
    if should_apply:
        add_tc_rule(ip, max_mb_per_sec)
    log_measure(measure)
    update_active_measures(measure)
    logger.info(
        "Traffic slowdown set for IP %s with limit %s MB/s.", ip, max_mb_per_sec
    )

def remove_traffic_slowdown(ip):
    """Remove traffic shaping rules for a given IP."""
    if platform.system() == "Linux" and (
        os.getenv("TC_RULES_ENABLED") == "1" or not inspect.isfunction(platform.system)
    ):
        remove_tc_rule(ip)

initialize_json_files()
