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
    # this folder has both individuals and households for 3 systems in it,
    # so there will be 3 unexpected files, but none missing
    expected_missing = 0
    expected_unexpected = 3
    actual_missing, actual_unexpected = c.validate_all_present()
    print("Expected Missing Files: " + str(expected_missing))
    print("Actual Missing Files:    " + str(len(actual_missing)))
    print("Expected Unexpected Files: " + str(expected_unexpected))
    print("Actual Unexpected Files:    " + str(len(actual_unexpected)))
    print(c.validate_all_present())
    assert len(actual_missing) == expected_missing
    assert len(actual_unexpected) == expected_unexpected
