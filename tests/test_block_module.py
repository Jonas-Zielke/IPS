import sys
import os
import json
import importlib
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Backend"))


def load_block_module(tmp_path):
    """Import Module.Block with working directory set to tmp_path."""
    logs_dir = tmp_path / "Logs"
    logs_dir.mkdir()
    cwd = os.getcwd()
    os.chdir(tmp_path)
    sys.modules.pop('Module.Block', None)
    try:
        mod = importlib.import_module('Module.Block')
        return mod, cwd
    except Exception:
        os.chdir(cwd)
        raise


def unload_block_module(cwd):
    os.chdir(cwd)
    sys.modules.pop('Module.Block', None)


def test_temp_block(tmp_path):
    Block, cwd = load_block_module(tmp_path)
    try:
        with patch.object(Block.platform, 'system', return_value='Linux'), \
             patch.object(Block.subprocess, 'run') as run_mock:
            Block.temp_block('1.1.1.1', 5, 'test')
        logs = Block.read_from_json(Block.block_log_file)
        active = Block.read_from_json(Block.active_measures_file)
    finally:
        unload_block_module(cwd)
    assert logs[-1]['ip'] == '1.1.1.1'
    assert logs[-1]['measure'] == 'temp_block'
    assert active[-1]['measure'] == 'temp_block'
    run_mock.assert_called_once_with(['sudo', 'iptables', '-A', 'INPUT', '-s', '1.1.1.1', '-j', 'DROP'], check=True)


def test_perma_block(tmp_path):
    Block, cwd = load_block_module(tmp_path)
    try:
        with patch.object(Block.platform, 'system', return_value='Linux'), \
             patch.object(Block.subprocess, 'run') as run_mock:
            Block.perma_block('2.2.2.2', 'reason')
        logs = Block.read_from_json(Block.block_log_file)
        active = Block.read_from_json(Block.active_measures_file)
    finally:
        unload_block_module(cwd)
    assert logs[-1]['ip'] == '2.2.2.2'
    assert logs[-1]['measure'] == 'perma_block'
    assert active[-1]['measure'] == 'perma_block'
    run_mock.assert_called_once_with(['sudo', 'iptables', '-A', 'INPUT', '-s', '2.2.2.2', '-j', 'DROP'], check=True)


def test_traffic_slowdown(tmp_path):
    Block, cwd = load_block_module(tmp_path)
    try:
        with patch.object(Block.subprocess, 'run') as run_mock:
            Block.traffic_slowdown('3.3.3.3', 10, 'slow')
        logs = Block.read_from_json(Block.block_log_file)
        active = Block.read_from_json(Block.active_measures_file)
    finally:
        unload_block_module(cwd)
    assert logs[-1]['ip'] == '3.3.3.3'
    assert logs[-1]['measure'] == 'traffic_slowdown'
    assert active[-1]['measure'] == 'traffic_slowdown'
    run_mock.assert_not_called()
