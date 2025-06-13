import sys, os, importlib
from unittest.mock import patch


def load_block(tmp_path):
    sys.modules.pop('Module.Block', None)
    logs_dir = tmp_path / "Logs"
    logs_dir.mkdir()
    (logs_dir / "block_log.json").write_text("[]")
    (logs_dir / "active_measures.json").write_text("[]")
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        mod = importlib.import_module('Module.Block')
        mod.block_log_file = str(logs_dir / "block_log.json")
        mod.active_measures_file = str(logs_dir / "active_measures.json")
        mod.initialize_json_files()
        return mod
    finally:
        os.chdir(cwd)


def test_traffic_slowdown_calls_tc(tmp_path):
    mod = load_block(tmp_path)
    with patch.object(mod.subprocess, 'run') as run_mock, \
         patch.object(mod.platform, 'system', return_value='Linux'):
        mod.traffic_slowdown('1.2.3.4', 5)
        assert any('tc' in call.args[0] for call in run_mock.call_args_list)


def test_remove_traffic_slowdown_calls_tc(tmp_path):
    mod = load_block(tmp_path)
    with patch.object(mod.subprocess, 'run') as run_mock, \
         patch.object(mod.platform, 'system', return_value='Linux'):
        mod.remove_traffic_slowdown('1.2.3.4')
        assert any('tc' in call.args[0] for call in run_mock.call_args_list)
