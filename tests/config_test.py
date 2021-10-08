import pytest
import util.config.config_util as cu


from dcctools.config import Configuration


def test_system_count():
    c = cu.get_config("tests/mock_setup/config.json")
    expected = 3
    found = c.system_count
    print("Expected: " + str(expected))
    print("Found:    " + str(found))
    assert (expected == found)


def test_validate_all_present():
    c = cu.get_config("tests/mock_setup/config.json")
    expected = 0
    found = len(c.validate_all_present())
    print("Expceted: " + str(expected))
    print("Found:    " + str(found))
    print(c.validate_all_present())
#    assert len(c.validate_all_present()) == 0
