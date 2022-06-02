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


def test_validate_config():
    c_single_thresh = cu.get_config("tests/mock_setup/config.json")
    actual_issues = c_single_thresh.validate_config()
    assert len(actual_issues) == 0
    n_expected_proj = 4
    n_expected_thresh = 3
    expected_issues = [
        f"Number of projects ({n_expected_proj}) and thresholds ({n_expected_thresh}) is unequal \
                \n\tThreshold must either be float or list of floats equal in length to the number of projects"
    ]

    c_multi_thresh = cu.get_config("tests/mock_setup/config-multi-threshold.json")
    actual_issues = c_multi_thresh.validate_config()
    assert len(expected_issues) == len(actual_issues)
    for i, expected_issue in enumerate(expected_issues):
        assert actual_issues[i] == expected_issue

    c_hh_no_thresh = cu.get_config("tests/mock_setup/config-hh-no-thresh.json")
    expected_issues = ["config file specifies household match without float household matching threshold"]
    actual_issues = c_hh_no_thresh.validate_config()
    assert len(expected_issues) == len(actual_issues)
    for i, expected_issue in enumerate(expected_issues):
        assert actual_issues[i] == expected_issue

