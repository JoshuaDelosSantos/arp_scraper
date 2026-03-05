from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import main


class TestMain:
    @patch("main.p.save_papers")
    @patch("main.p.fetch_paper")
    @patch("main.p.get_paper_ids", return_value=["id1", "id2"])
    @patch("main.time.sleep")
    @patch("main.config")
    def test_fetches_and_saves_papers(self, mock_config, mock_sleep, mock_get_ids, mock_fetch, mock_save):
        mock_config.LISTING_URL = "http://fake"
        mock_config.NUM_PAPERS = 2
        mock_config.DELAY = 0
        mock_config.OUTPUT_DIR = MagicMock(spec=Path)
        mock_config.OUTPUT_DIR.exists.return_value = True

        mock_fetch.side_effect = [
            {"id": "id1", "title": "T1", "authors": "", "abstract": "", "body": ""},
            {"id": "id2", "title": "T2", "authors": "", "abstract": "", "body": ""},
        ]

        main.main()

        assert mock_fetch.call_count == 2
        mock_save.assert_called_once()
        saved = mock_save.call_args[0][0]
        assert len(saved) == 2

    @patch("main.p.save_papers")
    @patch("main.p.get_paper_ids", return_value=[])
    @patch("main.config")
    def test_exits_early_when_no_ids(self, mock_config, mock_get_ids, mock_save):
        mock_config.LISTING_URL = "http://fake"
        mock_config.NUM_PAPERS = 5
        mock_config.DELAY = 0
        mock_config.OUTPUT_DIR = MagicMock(spec=Path)

        main.main()

        mock_save.assert_not_called()

    @patch("main.p.save_papers")
    @patch("main.p.fetch_paper", return_value=None)
    @patch("main.p.get_paper_ids", return_value=["id1"])
    @patch("main.time.sleep")
    @patch("main.config")
    def test_skips_none_returned_by_fetch(self, mock_config, mock_sleep, mock_get_ids, mock_fetch, mock_save):
        mock_config.LISTING_URL = "http://fake"
        mock_config.NUM_PAPERS = 1
        mock_config.DELAY = 0
        mock_config.OUTPUT_DIR = MagicMock(spec=Path)
        mock_config.OUTPUT_DIR.exists.return_value = True

        main.main()

        mock_save.assert_not_called()

    @patch("main.p.save_papers")
    @patch("main.p.fetch_paper", side_effect=Exception("network error"))
    @patch("main.p.get_paper_ids", return_value=["id1"])
    @patch("main.time.sleep")
    @patch("main.config")
    def test_handles_fetch_exception(self, mock_config, mock_sleep, mock_get_ids, mock_fetch, mock_save):
        mock_config.LISTING_URL = "http://fake"
        mock_config.NUM_PAPERS = 1
        mock_config.DELAY = 0
        mock_config.OUTPUT_DIR = MagicMock(spec=Path)
        mock_config.OUTPUT_DIR.exists.return_value = True

        main.main()

        mock_save.assert_not_called()

    @patch("main.p.save_papers")
    @patch("main.p.fetch_paper")
    @patch("main.p.get_paper_ids", return_value=["id1"])
    @patch("main.time.sleep")
    @patch("main.config")
    def test_creates_output_dir_if_missing(self, mock_config, mock_sleep, mock_get_ids, mock_fetch, mock_save):
        mock_config.LISTING_URL = "http://fake"
        mock_config.NUM_PAPERS = 1
        mock_config.DELAY = 0
        mock_config.OUTPUT_DIR = MagicMock(spec=Path)
        mock_config.OUTPUT_DIR.exists.return_value = False

        mock_fetch.return_value = {"id": "id1", "title": "", "authors": "", "abstract": "", "body": ""}

        main.main()

        mock_config.OUTPUT_DIR.mkdir.assert_called_once_with(parents=True)
