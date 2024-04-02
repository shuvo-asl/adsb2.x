"""
adsb2.x/src/tests/test_config.py
"""
import pytest
from core.Config import Config

class TestConfig():
    
    def test_config_get_success(self):
        config = Config()
        result = config.get("sys")
        assert result is not None

    def test_config_get_key_error(self):
        config = Config.getInstance()
        try:
            result = config.get("nonexistent_key")
            assert False, "Expected KeyError, but no exception was raised"
        except KeyError:
            assert True
    
    def test_config_get_child_key(self):
        config = Config.getInstance()
        try:
            result = config.get('sys.tracking_mode')
            assert result is not None;
        except KeyError:
            assert False, "Un Expected Key Error or system could not parse the key"
        