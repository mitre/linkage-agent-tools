import pytest
from match import MissingResults, has_results_available, do_match

class MockConfiguration:
    def __init__(self, tmp_dir, projects, household_match=False):
        self.project_results_dir = tmp_dir
        self.projects = projects
        self.household_match = household_match

    mongo_uri = "http://example.com"
    systems = []

class MockResults:
    def __init__(self, systems, project, results):
        pass

    def insert_results(self, collection):
        pass

class MockMongo:
    def __init__(self, mongo_uri):
        self.linkage_agent = type('', (), dict(match_groups=None,house_hold_match_groups=None))

def test_has_results_available(tmp_path):
    d = tmp_path / 'codi_test_results'

    d.mkdir()
    (d / 'foo.json').touch()
    (d / 'bar.json').touch()
    (d / 'quz.json').touch()
    print(str(d))

    print(str(d) + "FIND ME")
    with pytest.raises(MissingResults, match="Missing results for projects: baz"):
        has_results_available(MockConfiguration(str(d), ['foo', 'bar', 'baz']))

def test_do_match(mocker, monkeypatch, tmp_path):

    d = tmp_path / 'codi_test_results'
    d.mkdir()
    content = "{}"
    (d / 'foo.json').write_text(content)
    (d / 'bar.json').write_text(content)
    (d / 'quz.json').write_text(content)

    monkeypatch.setattr("match.Results", MockResults)
    monkeypatch.setattr("match.MongoClient", MockMongo)

    do_match(MockConfiguration(str(d), ['foo', 'bar', 'quz']))
    # Test with household_match = True
    do_match(MockConfiguration(str(d), ['foo', 'bar', 'quz'], True))
