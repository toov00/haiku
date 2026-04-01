import subprocess
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest

from haiku.clipboard import copy_text


class TestCopyText:
    @patch("haiku.clipboard.subprocess.run")
    @patch("haiku.clipboard.sys.platform", "darwin")
    def test_pbcopy_on_macos(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock()
        assert copy_text("one\ntwo\nthree") is True
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert args[0] == ["pbcopy"]
        assert kwargs["input"] == "one\ntwo\nthree\n"
        assert kwargs["text"] is True

    @patch("haiku.clipboard.subprocess.run")
    @patch("haiku.clipboard.shutil.which")
    @patch("haiku.clipboard.sys.platform", "linux")
    def test_xclip_when_available(self, mock_which: MagicMock, mock_run: MagicMock) -> None:
        def which(name: str) -> Optional[str]:
            if name == "wl-copy":
                return None
            if name == "xclip":
                return "/usr/bin/xclip"
            return None

        mock_which.side_effect = which
        mock_run.return_value = MagicMock()
        assert copy_text("a") is True
        mock_run.assert_called_once()
        assert mock_run.call_args[0][0] == ["xclip", "-selection", "clipboard"]

    @patch("haiku.clipboard.subprocess.run")
    @patch("haiku.clipboard.shutil.which")
    @patch("haiku.clipboard.sys.platform", "linux")
    def test_wl_copy_preferred_over_xclip(
        self, mock_which: MagicMock, mock_run: MagicMock
    ) -> None:
        def which_side_effect(name: str) -> Optional[str]:
            if name == "wl-copy":
                return "/usr/bin/wl-copy"
            if name == "xclip":
                return "/usr/bin/xclip"
            return None

        mock_which.side_effect = which_side_effect
        mock_run.return_value = MagicMock()
        assert copy_text("x") is True
        assert mock_run.call_args[0][0] == ["wl-copy"]

    @patch("haiku.clipboard.shutil.which", return_value=None)
    @patch("haiku.clipboard.sys.platform", "linux")
    def test_linux_no_tool_returns_false(self, mock_which: MagicMock) -> None:
        assert copy_text("hi") is False

    @patch("haiku.clipboard.subprocess.run")
    @patch("haiku.clipboard.sys.platform", "win32")
    def test_clip_on_windows(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock()
        assert copy_text("line\n") is True
        mock_run.assert_called_once()
        kwargs = mock_run.call_args[1]
        assert kwargs["input"] == "line\n".encode("utf-16-le")

    @patch("haiku.clipboard.subprocess.run", side_effect=subprocess.CalledProcessError(1, "pbcopy"))
    @patch("haiku.clipboard.sys.platform", "darwin")
    def test_returns_false_on_failure(self, mock_run: MagicMock) -> None:
        assert copy_text("fail") is False

    def test_empty_string_returns_false(self) -> None:
        assert copy_text("") is False
