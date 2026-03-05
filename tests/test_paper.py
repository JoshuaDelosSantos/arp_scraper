import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

import paper as p


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_HTML = """
<html>
<head><title>Test Paper</title></head>
<body>
  <header>Site header</header>
  <nav>Navigation</nav>
  <h1 class="ltx_title">Title:Sample Paper Title</h1>
  <div class="ltx_authors">Alice, Bob</div>
  <div class="ltx_abstract">Abstract
This is the abstract.</div>
  <p>Body paragraph one.</p>
  <script>var x = 1;</script>
  <style>.cls{}</style>
  <footer>Site footer</footer>
</body>
</html>
"""

LISTING_HTML = """
<html><body>
  <a href="/abs/2501.00001">Paper 1</a>
  <a href="/abs/2501.00002">Paper 2</a>
  <a href="/abs/2501.00003">Paper 3</a>
  <a href="/abs/2501.00004">Paper 4</a>
  <a href="/abs/2501.00005">Paper 5</a>
</body></html>
"""


def _make_paper(paper_id: str = "2501.00001") -> dict:
    return {
        "id": paper_id,
        "title": "Sample Paper Title",
        "authors": "Alice, Bob",
        "abstract": "This is the abstract.",
        "body": "Body paragraph one.",
    }


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    """Provides an empty temporary output directory."""
    d = tmp_path / "papers"
    d.mkdir()
    return d


@pytest.fixture
def papers_json(output_dir: Path) -> Path:
    """Writes a pre-existing papers.json with one paper and returns the path."""
    filepath = output_dir / "papers.json"
    filepath.write_text(json.dumps([_make_paper("existing_001")], indent=2), encoding="utf-8")
    return filepath


# ---------------------------------------------------------------------------
# load_papers
# ---------------------------------------------------------------------------

class TestLoadPapers:
    def test_returns_empty_list_when_file_missing(self, output_dir):
        result = p.load_papers(str(output_dir))
        assert result == []

    def test_loads_existing_papers(self, output_dir, papers_json):
        result = p.load_papers(str(output_dir))
        assert len(result) == 1
        assert result[0]["id"] == "existing_001"


# ---------------------------------------------------------------------------
# save_papers
# ---------------------------------------------------------------------------

class TestSavePapers:
    def test_saves_new_papers_to_empty_dir(self, output_dir):
        papers = [_make_paper("p1"), _make_paper("p2")]
        p.save_papers(papers, str(output_dir))

        filepath = output_dir / "papers.json"
        assert filepath.exists()
        saved = json.loads(filepath.read_text(encoding="utf-8"))
        assert len(saved) == 2
        assert {paper["id"] for paper in saved} == {"p1", "p2"}

    def test_merges_with_existing_without_duplicates(self, output_dir, papers_json):
        new_papers = [_make_paper("existing_001"), _make_paper("new_001")]
        p.save_papers(new_papers, str(output_dir))

        saved = json.loads(papers_json.read_text(encoding="utf-8"))
        assert len(saved) == 2
        ids = {paper["id"] for paper in saved}
        assert ids == {"existing_001", "new_001"}

    def test_no_new_papers_still_writes(self, output_dir, papers_json):
        p.save_papers([_make_paper("existing_001")], str(output_dir))
        saved = json.loads(papers_json.read_text(encoding="utf-8"))
        assert len(saved) == 1


# ---------------------------------------------------------------------------
# fetch_paper
# ---------------------------------------------------------------------------

class TestFetchPaper:
    @patch("paper.requests.get")
    def test_returns_structured_dict(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_HTML
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = p.fetch_paper("2501.00001")

        assert result is not None
        assert result["id"] == "2501.00001"
        assert result["title"] == "Sample Paper Title"
        assert result["authors"] == "Alice, Bob"
        assert "abstract" in result["abstract"].lower() or "This is the abstract" in result["abstract"]
        assert isinstance(result["body"], str)
        assert len(result["body"]) > 0

    @patch("paper.requests.get")
    def test_returns_none_on_http_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        result = p.fetch_paper("bad_id")
        assert result is None

    @patch("paper.requests.get")
    def test_handles_missing_tags_gracefully(self, mock_get):
        """If the HTML has no title/authors/abstract tags, fields default to empty strings."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><p>Just some text</p></body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = p.fetch_paper("2501.00099")
        assert result is not None
        assert result["title"] == ""
        assert result["authors"] == ""
        assert result["abstract"] == ""


# ---------------------------------------------------------------------------
# get_paper_ids
# ---------------------------------------------------------------------------

class TestGetPaperIds:
    @patch("paper.load_papers", return_value=[])
    @patch("paper.requests.get")
    def test_returns_requested_number_of_ids(self, mock_get, _mock_load):
        mock_response = MagicMock()
        mock_response.text = LISTING_HTML
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        ids = p.get_paper_ids("http://fake-url", 3)
        assert len(ids) == 3
        assert ids[0] == "2501.00001"

    @patch("paper.load_papers", return_value=[{"id": "2501.00001"}])
    @patch("paper.requests.get")
    def test_skips_existing_ids(self, mock_get, _mock_load):
        mock_response = MagicMock()
        mock_response.text = LISTING_HTML
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        ids = p.get_paper_ids("http://fake-url", 3)
        assert "2501.00001" not in ids
        assert len(ids) == 3

    @patch("paper.load_papers", return_value=[])
    @patch("paper.requests.get")
    def test_returns_empty_list_when_no_links(self, mock_get, _mock_load):
        mock_response = MagicMock()
        mock_response.text = "<html><body>No papers here</body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        ids = p.get_paper_ids("http://fake-url", 5)
        assert ids == []

    @patch("paper.load_papers", return_value=[])
    @patch("paper.requests.get")
    def test_no_duplicate_ids(self, mock_get, _mock_load):
        dup_html = """
        <html><body>
          <a href="/abs/2501.00001">Link 1</a>
          <a href="/abs/2501.00001">Link 1 duplicate</a>
          <a href="/abs/2501.00002">Link 2</a>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.text = dup_html
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        ids = p.get_paper_ids("http://fake-url", 5)
        assert ids == ["2501.00001", "2501.00002"]
