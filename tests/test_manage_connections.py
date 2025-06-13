import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Backend"))
import importlib
from unittest.mock import patch


def load_module_without_thread(tmp_path):
    sys.modules.pop('Module.Manage_Connections', None)
    logs_dir = tmp_path / "Logs"
    logs_dir.mkdir()
    (logs_dir / "active_connections.json").write_text("[]")
    with patch('threading.Thread.start', lambda self: None):
        cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            mod = importlib.import_module('Module.Manage_Connections')
            mod.ConnectionManager.write_to_json = lambda self: None
            return mod
        finally:
            os.chdir(cwd)


def test_add_and_remove_connection(tmp_path):
    mc = load_module_without_thread(tmp_path)
    file = tmp_path / 'conns.json'
    manager = mc.ConnectionManager(timeout=1, active_connections_file=str(file))
    manager.add_connection('1.1.1.1', 1000, '2.2.2.2', 80)
    assert ('1.1.1.1', 1000, '2.2.2.2', 80) in manager.connections
    manager.remove_connection('1.1.1.1', 1000, '2.2.2.2', 80)
    assert not manager.connections


def test_close_connection_sends_rst(tmp_path):
    mc = load_module_without_thread(tmp_path)
    file = tmp_path / 'conns.json'
    manager = mc.ConnectionManager(timeout=1, active_connections_file=str(file))
    with patch.object(mc, 'send') as send_mock:
        manager.close_connection('1.1.1.1', 1000, '2.2.2.2', 80)
        send_mock.assert_called_once()
