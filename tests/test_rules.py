import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Backend"))
from unittest.mock import patch
import importlib

def import_rules(tmp_path):
    logs_dir = tmp_path / "Logs"
    logs_dir.mkdir()
    (logs_dir / "active_connections.json").write_text("[]")
    with patch('threading.Thread.start', lambda self: None):
        cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            if 'Module.Rules' in sys.modules:
                del sys.modules['Module.Rules']
            if 'Module.Manage_Connections' in sys.modules:
                del sys.modules['Module.Manage_Connections']
            return importlib.import_module('Module.Rules')
        finally:
            os.chdir(cwd)


def test_detect_denamysch_ip_blocks(tmp_path):
    Rules = import_rules(tmp_path)
    entry = {'ip_src': '203.0.113.5'}
    with patch('Module.Rules.Block.perma_block') as pb:
        Rules.detect_denamysch_ip(None, entry)
        pb.assert_called_once_with('203.0.113.5', 'Denamysch range')


def test_detect_sql_injection(tmp_path):
    Rules = import_rules(tmp_path)
    entry = {'ip_src': '1.2.3.4', 'payload': 'SELECT * FROM users'}
    with patch('Module.Rules.Block.temp_block') as tb:
        Rules.detect_sql_injection(None, entry)
        tb.assert_called_once()


def test_detect_xss(tmp_path):
    Rules = import_rules(tmp_path)
    entry = {'ip_src': '1.2.3.4', 'payload': '<script>alert(1)</script>'}
    with patch('Module.Rules.Block.temp_block') as tb:
        Rules.detect_xss(None, entry)
        tb.assert_called_once()


def test_detect_bruteforce(monkeypatch, tmp_path):
    Rules = import_rules(tmp_path)
    entry = {'ip_src': '1.1.1.1', 'payload': 'POST /login'}
    monkeypatch.setattr(Rules, 'BRUTE_FORCE_THRESHOLD', 2)
    with patch('Module.Rules.Block.temp_block') as tb:
        Rules.detect_bruteforce(None, entry)
        Rules.detect_bruteforce(None, entry)
        tb.assert_called_once()
