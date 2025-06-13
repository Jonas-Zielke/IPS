import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Backend"))
from fastapi.testclient import TestClient
from Module.API.API import app, read_json_file
from unittest.mock import patch
import Module.API.API as api

client = TestClient(app)


def test_read_json_file_missing(tmp_path):
    file = tmp_path / "missing.json"
    assert read_json_file(file) == []


def test_logs_endpoint():
    with patch('Module.API.API.read_json_file', return_value=[{"ok": True}]):
        response = client.get('/logs/blocks')
        assert response.status_code == 200
        assert response.json() == [{"ok": True}]


def test_resource_usage_endpoint():
    with patch('Module.API.API.ResourceManager.get_cpu_usage', return_value=1), \
         patch('Module.API.API.ResourceManager.get_ram_usage', return_value=2), \
         patch('Module.API.API.ResourceManager.get_network_traffic', return_value={'bytes_sent':3,'bytes_received':4}):
        response = client.get('/resource/usage')
        assert response.status_code == 200
        assert response.json() == {
            'cpu_usage': 1,
            'ram_usage': 2,
            'network_traffic': {'bytes_sent':3,'bytes_received':4}
        }
