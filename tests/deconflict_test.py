import pytest

from dcctools.deconflict import deconflict, link_count

example_result = {
    "a": [142],
    "b": [142, 280],
    "run_results": [
        {"a": 142, "b": 142, "project": "name-sex-dob-zip"},
        {"a": 142, "b": 280, "project": "name-sex-dob-zip"},
        {"a": 142, "b": 142, "project": "name-sex-dob-phone"},
        {"a": 142, "b": 280, "project": "name-sex-dob-phone"},
        {"a": 142, "b": 142, "project": "name-sex-dob-addr"},
        {"a": 142, "b": 280, "project": "name-sex-dob-addr"},
        {"a": 142, "b": 142, "project": "name-sex-dob-parents"},
        {"a": 142, "b": 280, "project": "name-sex-dob-parents"},
        {"a": 142, "c": 142, "project": "name-sex-dob-zip"},
        {"a": 142, "c": 142, "project": "name-sex-dob-phone"},
        {"a": 142, "c": 142, "project": "name-sex-dob-addr"},
        {"b": 142, "c": 142, "project": "name-sex-dob-zip"},
        {"b": 142, "c": 142, "project": "name-sex-dob-phone"},
        {"b": 142, "c": 142, "project": "name-sex-dob-addr"},
        {"b": 142, "c": 142, "project": "name-sex-dob-parents"},
    ],
    "c": [142],
}

example_result_no_c = {
    "a": [142],
    "b": [142, 280],
    "run_results": [
        {"a": 142, "b": 142, "project": "name-sex-dob-zip"},
        {"a": 142, "b": 280, "project": "name-sex-dob-zip"},
        {"a": 142, "b": 142, "project": "name-sex-dob-phone"},
        {"a": 142, "b": 280, "project": "name-sex-dob-phone"},
        {"a": 142, "b": 142, "project": "name-sex-dob-addr"},
        {"a": 142, "b": 280, "project": "name-sex-dob-addr"},
        {"a": 142, "b": 142, "project": "name-sex-dob-parents"},
        {"a": 142, "b": 280, "project": "name-sex-dob-parents"},
    ],
}


def test_link_count():
    count = link_count(example_result, "b", 142)
    assert count == 8


def test_deconflict():
    deconflicted_record = deconflict(example_result, ["a", "b", "c"])
    assert deconflicted_record["a"] == 142
    assert deconflicted_record["b"] == 142
    assert deconflicted_record["c"] == 142


def test_deconflict_with_missing_system():
    deconflicted_record = deconflict(example_result_no_c, ["a", "b", "c"])
    assert deconflicted_record["a"] == 142
    assert deconflicted_record["b"] == 142
