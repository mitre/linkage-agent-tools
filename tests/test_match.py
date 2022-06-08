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
        self.linkage_agent = type('', (), dict(match_groups=None, household_match_groups=None))

@pytest.mark.parametrize('available,expected,result', [
    pytest.param(['foo', 'bar', 'quz'], ['foo', 'bar', 'quz'], True),  # Exact match
    pytest.param(['foo', 'bar', 'quz', 'cat'], ['foo', 'bar', 'quz'], True),  # Subset
    pytest.param(['foo', 'bar', 'cat'], ['foo', 'bar', 'baz'], False),  # Missing `baz`
])
def test_has_results_available(tmp_path, available, expected, result):
    d = tmp_path / 'codi_test_results'
    d.mkdir()
    for file in available:
        (d / f'{file}.json').touch()

    if result:
        assert has_results_available(MockConfiguration(str(d), expected))
        # Configuration should be ignored when projects are specifically passed in
        assert has_results_available(MockConfiguration(str(d), ['fake']), expected)
    else:
        with pytest.raises(MissingResults, match="Missing results for projects: baz"):
            has_results_available(MockConfiguration(str(d), expected))
        with pytest.raises(MissingResults, match="Missing results for projects: baz"):
            has_results_available(MockConfiguration(str(d), ['fake']), expected)

@pytest.mark.parametrize('available,expected,household,result', [
    pytest.param(['foo', 'bar', 'quz'], ['foo', 'bar', 'quz'], False, True),
    pytest.param(['foo', 'bar', 'quz', 'cat'], ['foo', 'bar', 'quz'], False, True),
    pytest.param(['foo', 'bar', 'cat'], ['foo', 'bar', 'quz'], False, False),
    # HouseHold Tests
    pytest.param(['fn-phone-addr-zip'], ['fn-phone-addr-zip'], True, True),
    pytest.param(['fn-phone-addr-zip'], ['foo'], True, True),
    pytest.param(['fn-phone-addr-zip', 'bar'], ['foo'], True, True),
    pytest.param(['foo'], ['fn-phone-addr-zip'], True, False),
])
def test_do_match(monkeypatch, tmp_path, available, expected, household, result):
    d = tmp_path / 'codi_test_results'
    d.mkdir()
    content = "{}"
    for file in available:
        (d / f'{file}.json').write_text(content)

    monkeypatch.setattr("match.Results", MockResults)
    monkeypatch.setattr("match.MongoClient", MockMongo)

    try:
        do_match(MockConfiguration(str(d), expected, household))
        # Configuration should be ignored when projects are specifically passed in
        do_match(MockConfiguration(str(d), ['fake'], household), expected)
        assert result
    except MissingResults:
        assert not result
