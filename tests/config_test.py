import pytest

from dcctools.config import Configuration


def test_system_count():
    c = Configuration("tests/mock_setup/config.json")
    assert c.system_count() == 2


def test_validate_all_present():
    c = Configuration("tests/mock_setup/config.json")
    assert c.validate_all_present()
