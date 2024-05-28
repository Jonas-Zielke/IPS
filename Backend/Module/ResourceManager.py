import psutil

class ResourceManager:
    @staticmethod
    def get_cpu_usage():
        """
        Gibt die aktuelle CPU-Auslastung in Prozent zurück.
        """
        return psutil.cpu_percent(interval=1)

    @staticmethod
    def get_ram_usage():
        """
        Gibt die aktuelle RAM-Auslastung in Prozent zurück.
        """
        memory_info = psutil.virtual_memory()
        return memory_info.percent

    @staticmethod
    def get_network_traffic():
        """
        Gibt die aktuelle Netzwerkverkehrsauslastung in Bytes zurück.
        """
        net_io = psutil.net_io_counters()
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_received': net_io.bytes_recv
        }
