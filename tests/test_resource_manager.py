import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Backend"))
import Module.ResourceManager as rm


def test_cpu_usage_range():
    usage = rm.ResourceManager.get_cpu_usage()
    assert isinstance(usage, (int, float))
    assert 0 <= usage <= 100


def test_ram_usage_range():
    usage = rm.ResourceManager.get_ram_usage()
    assert isinstance(usage, (int, float))
    assert 0 <= usage <= 100


def test_network_traffic_keys():
    data = rm.ResourceManager.get_network_traffic()
    assert 'bytes_sent' in data and 'bytes_received' in data
    assert isinstance(data['bytes_sent'], int)
    assert isinstance(data['bytes_received'], int)
