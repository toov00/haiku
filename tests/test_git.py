import subprocess
from unittest.mock import MagicMock, patch

import pytest

from haiku.git import GitError, get_last_diff, get_last_commit_message


SAMPLE_DIFF = """\
diff --git a/hello.py b/hello.py
index e69de29..d95f3ad 100644
--- a/hello.py
+++ b/hello.py
@@ -0,0 +1,3 @@
+def greet(name: str) -> str:
+    return f"hello, {name}"
+
"""


class TestGetLastDiff:
    def _mock_run(self, stdout: str = SAMPLE_DIFF, returncode: int = 0) -> MagicMock:
        result = MagicMock()
        result.stdout = stdout
        result.returncode = returncode
        return result

    @patch("haiku.git.subprocess.run")
    def test_returns_diff_from_last_commit(self, mock_run: MagicMock) -> None:
        mock_run.return_value = self._mock_run()
        diff = get_last_diff(staged=False)
        assert "def greet" in diff
        cmd = mock_run.call_args[0][0]
        assert cmd == ["git", "diff", "HEAD~1", "HEAD"]

    @patch("haiku.git.subprocess.run")
    def test_returns_staged_diff(self, mock_run: MagicMock) -> None:
        mock_run.return_value = self._mock_run()
        get_last_diff(staged=True)
        cmd = mock_run.call_args[0][0]
        assert cmd == ["git", "diff", "--cached"]

    @patch("haiku.git.subprocess.run")
    def test_raises_git_error_on_nonzero_exit(self, mock_run: MagicMock) -> None:
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=128, cmd=["git", "diff"], stderr="not a git repository"
        )
        with pytest.raises(GitError, match="not a git repository"):
            get_last_diff()

    @patch("haiku.git.subprocess.run")
    def test_raises_git_error_when_git_missing(self, mock_run: MagicMock) -> None:
        mock_run.side_effect = FileNotFoundError()
        with pytest.raises(GitError, match="not found on PATH"):
            get_last_diff()

    @patch("haiku.git.subprocess.run")
    def test_truncates_large_diffs(self, mock_run: MagicMock) -> None:
        big_diff = "x" * 20_000
        mock_run.return_value = self._mock_run(stdout=big_diff)
        result = get_last_diff(max_bytes=100)
        assert len(result.encode()) <= 200  # some slack for the notice
        assert "truncated" in result

    @patch("haiku.git.subprocess.run")
    def test_does_not_truncate_small_diffs(self, mock_run: MagicMock) -> None:
        mock_run.return_value = self._mock_run(stdout=SAMPLE_DIFF)
        result = get_last_diff(max_bytes=8_000)
        assert result == SAMPLE_DIFF


class TestGetLastCommitMessage:
    @patch("haiku.git.subprocess.run")
    def test_returns_last_commit_message(self, mock_run: MagicMock) -> None:
        result = MagicMock()
        result.stdout = "Add feature X\n\nDetails here\n"
        mock_run.return_value = result

        message = get_last_commit_message()

        cmd = mock_run.call_args[0][0]
        assert cmd == ["git", "log", "-1", "--pretty=%B"]
        assert message == "Add feature X\n\nDetails here"

    @patch("haiku.git.subprocess.run")
    def test_raises_git_error_on_failure(self, mock_run: MagicMock) -> None:
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["git", "log", "-1", "--pretty=%B"],
            stderr="some git error",
        )

        with pytest.raises(GitError, match="some git error"):
            get_last_commit_message()
