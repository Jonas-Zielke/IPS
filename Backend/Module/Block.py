import json
from datetime import datetime, timedelta
import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Config import EXCLUDED_IP_RANGES

block_log_file = 'Logs/block_log.json'
active_measures_file = 'Logs/active_measures.json'

def initialize_json_files():
    with open(block_log_file, 'w') as f:
        json.dump([], f)
    with open(active_measures_file, 'w') as f:
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
    write_to_json(block_log_file, logs)

def update_active_measures(measure):
    active_measures = read_from_json(active_measures_file)
    active_measures.append(measure)
    write_to_json(active_measures_file, active_measures)

def is_ip_excluded(ip):
    return any(ip.startswith(prefix) for prefix in EXCLUDED_IP_RANGES)

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
    log_measure(measure)
    update_active_measures(measure)
    print(f"Temporary block set for IP {ip} for {duration_minutes} minutes.")

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
    log_measure(measure)
    update_active_measures(measure)
    print(f"Permanent block set for IP {ip}.")

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
    log_measure(measure)
    update_active_measures(measure)
    print(f"Traffic slowdown set for IP {ip} with limit {max_mb_per_sec} MB/s.")

initialize_json_files()
