import time
import json
import logging
from scapy.all import send, IP, TCP
from threading import Thread, Lock
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self, timeout, active_connections_file='Logs/active_connections.json'):
        self.timeout = timeout
        self.connections = {}
        self.lock = Lock()
        self.active_connections_file = active_connections_file
        self.initialize_json_file()

    def initialize_json_file(self):
        with open(self.active_connections_file, 'w') as f:
            json.dump([], f)

    def write_to_json(self):
        with self.lock:
            connections_list = [
                {
                    "src_ip": conn[0],
                    "src_port": conn[1],
                    "dst_ip": conn[2],
                    "dst_port": conn[3],
                    "timestamp": datetime.fromtimestamp(timestamp).isoformat()
                }
                for conn, timestamp in self.connections.items()
            ]
            from Config import MAX_LOG_RECORDS
            if len(connections_list) > MAX_LOG_RECORDS:
                connections_list = connections_list[-MAX_LOG_RECORDS:]
            with open(self.active_connections_file, 'w') as f:
                json.dump(connections_list, f, indent=4)

    def add_connection(self, src_ip, src_port, dst_ip, dst_port):
        with self.lock:
            self.connections[(src_ip, src_port, dst_ip, dst_port)] = time.time()
            self.write_to_json()

    def remove_connection(self, src_ip, src_port, dst_ip, dst_port):
        with self.lock:
            if (src_ip, src_port, dst_ip, dst_port) in self.connections:
                del self.connections[(src_ip, src_port, dst_ip, dst_port)]
                self.write_to_json()

    def check_connections(self):
        while True:
            current_time = time.time()
            to_remove = []
            with self.lock:
                for conn, timestamp in self.connections.items():
                    if current_time - timestamp > self.timeout:
                        to_remove.append(conn)
            for conn in to_remove:
                src_ip, src_port, dst_ip, dst_port = conn
                self.close_connection(src_ip, src_port, dst_ip, dst_port)
                self.remove_connection(src_ip, src_port, dst_ip, dst_port)
            time.sleep(1)

    def close_connection(self, src_ip, src_port, dst_ip, dst_port):
        rst_packet = IP(src=src_ip, dst=dst_ip) / TCP(sport=src_port, dport=dst_port, flags='R')
        send(rst_packet)
        logger.info(
            "Closed incomplete connection from %s:%s to %s:%s",
            src_ip,
            src_port,
            dst_ip,
            dst_port,
        )

    def start(self):
        Thread(target=self.check_connections, daemon=True).start()

# Initialisiere den ConnectionManager mit einem Timeout aus der Config
from Config import SYN_FLOOD_TIMEOUT

connection_manager = None


def get_connection_manager():
    """Create the global ConnectionManager on first use and start it."""
    global connection_manager
    if connection_manager is None:
        connection_manager = ConnectionManager(SYN_FLOOD_TIMEOUT)
        connection_manager.start()
    return connection_manager


if __name__ == "__main__":
    get_connection_manager()
