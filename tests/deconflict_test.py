import pytest
from dcctools.deconflict import average_link_strength, link_count, deconflict

example_result = {
    "a" : [
        142
    ],
    "b" : [
        142,
        280
    ],
    "links" : [
        {
            "a" : 142,
            "b" : 142,
            "run_name" : "name-sex-dob-zip",
            "score" : 0.971112999150382
        },
        {
            "a" : 142,
            "b" : 280,
            "run_name" : "name-sex-dob-zip",
            "score" : 0.777118644067797
        },
        {
            "a" : 142,
            "b" : 142,
            "run_name" : "name-sex-dob-phone",
            "score" : 0.939367311072056
        },
        {
            "a" : 142,
            "b" : 280,
            "run_name" : "name-sex-dob-phone",
            "score" : 0.768828907270353
        },
        {
            "a" : 142,
            "b" : 142,
            "run_name" : "name-sex-dob-addr",
            "score" : 0.916524701873935
        },
        {
            "a" : 142,
            "b" : 280,
            "run_name" : "name-sex-dob-addr",
            "score" : 0.775752437473506
        },
        {
            "a" : 142,
            "b" : 142,
            "run_name" : "name-sex-dob-parents",
            "score" : 0.897427754842807
        },
        {
            "a" : 142,
            "b" : 280,
            "run_name" : "name-sex-dob-parents",
            "score" : 0.852218321097989
        },
        {
            "a" : 142,
            "c" : 142,
            "run_name" : "name-sex-dob-zip",
            "score" : 0.813863928112965
        },
        {
            "a" : 142,
            "c" : 142,
            "run_name" : "name-sex-dob-phone",
            "score" : 0.771681415929204
        },
        {
            "a" : 142,
            "c" : 142,
            "run_name" : "name-sex-dob-addr",
            "score" : 0.793965517241379
        },
        {
            "b" : 142,
            "c" : 142,
            "run_name" : "name-sex-dob-zip",
            "score" : 0.841113490364026
        },
        {
            "b" : 142,
            "c" : 142,
            "run_name" : "name-sex-dob-phone",
            "score" : 0.82963620230701
        },
        {
            "b" : 142,
            "c" : 142,
            "run_name" : "name-sex-dob-addr",
            "score" : 0.805172413793103
        },
        {
            "b" : 142,
            "c" : 142,
            "run_name" : "name-sex-dob-parents",
            "score" : 0.772885650934431
        }
    ],
    "c" : [
        142
    ]
}

def test_average_link_strength():
  average = average_link_strength(example_result, 'b', 142)
  assert average == pytest.approx(0.871655066)

def test_link_count():
  count = link_count(example_result, 'b', 142)
  assert count == 8

def test_deconflict():
  deconflicted_record = deconflict(example_result, ['a', 'b', 'c'])
  assert deconflicted_record['a'] == 142
  assert deconflicted_record['b'] == 142
  assert deconflicted_record['c'] == 142
