import pytest

from match import MissingResults, has_results_available

class MockConfiguration:
    def __init__(self, tmp_dir):
        self.tmp_dir = tmp_dir

    projects = ['foo', 'bar', 'baz']

    @property
    def project_results_dir(self):
        return self.tmp_dir

def test_has_results_available(tmp_path):
    d = tmp_path / 'codi_test_results'

    d.mkdir()
    (d / 'foo.json').touch()
    (d / 'bar.json').touch()
    (d / 'quz.json').touch()
    print(str(d))

    print(str(d) + "FIND ME")
    with pytest.raises(MissingResults, match="Missing results for projects: baz"):
        has_results_available(MockConfiguration(str(d)))
