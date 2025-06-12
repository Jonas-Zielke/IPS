"""Utility functions for blocking or slowing down network traffic."""

import json
from datetime import datetime, timedelta
import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Config import EXCLUDED_IP_RANGES

block_log_file = 'Logs/block_log.json'
active_measures_file = 'Logs/active_measures.json'

def initialize_json_files() -> None:
    """Create empty JSON files used for logging block measures."""

    with open(block_log_file, "w") as f:
        json.dump([], f)
    with open(active_measures_file, "w") as f:
        json.dump([], f)

def write_to_json(file: str, data) -> None:
    """Write ``data`` to ``file`` as formatted JSON."""

    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def read_from_json(file: str):
    """Return JSON data from ``file``."""

    with open(file, "r") as f:
        return json.load(f)

def log_measure(measure: dict) -> None:
    """Append a measure to the block log."""

    logs = read_from_json(block_log_file)
    logs.append(measure)
    write_to_json(block_log_file, logs)

def update_active_measures(measure: dict) -> None:
    """Add a measure to the list of active measures."""

    active_measures = read_from_json(active_measures_file)
    active_measures.append(measure)
    write_to_json(active_measures_file, active_measures)

def is_ip_excluded(ip: str) -> bool:
    """Check whether ``ip`` falls into an excluded range."""

    return any(ip.startswith(prefix) for prefix in EXCLUDED_IP_RANGES)

def temp_block(ip: str, duration_minutes: int, reason: str | None = None) -> None:
    """Temporarily block ``ip`` for ``duration_minutes`` minutes."""

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
    log_measure(measure)
    update_active_measures(measure)
    print(f"Temporary block set for IP {ip} for {duration_minutes} minutes.")

def perma_block(ip: str, reason: str | None = None) -> None:
    """Permanently block ``ip``."""

    if is_ip_excluded(ip):
        return
    measure = {
        "ip": ip,
        "measure": "perma_block",
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "reason": reason
    }
    log_measure(measure)
    update_active_measures(measure)
    print(f"Permanent block set for IP {ip}.")

def traffic_slowdown(ip: str, max_mb_per_sec: int, reason: str | None = None) -> None:
    """Limit ``ip`` to ``max_mb_per_sec`` megabytes per second."""

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
    log_measure(measure)
    update_active_measures(measure)
    print(f"Traffic slowdown set for IP {ip} with limit {max_mb_per_sec} MB/s.")

initialize_json_files()
