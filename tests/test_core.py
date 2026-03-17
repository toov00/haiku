from unittest.mock import MagicMock, patch

import pytest

from haiku.core import generate_haiku, _clean


class TestClean:
    def test_returns_three_lines(self) -> None:
        raw = "old code drifts away\nrefactored into the wind\ngit blame forgets"
        assert _clean(raw) == raw

    def test_strips_blank_lines(self) -> None:
        raw = "\nfirst line here\n\nsecond line here\n\nthird line here\n"
        result = _clean(raw)
        assert result.count("\n") == 2

    def test_trims_extra_lines(self) -> None:
        raw = "line one\nline two\nline three\nbonus line"
        result = _clean(raw)
        assert len(result.splitlines()) == 3

    def test_raises_on_too_few_lines(self) -> None:
        with pytest.raises(ValueError, match="Expected 3"):
            _clean("only one line")


class TestGenerateHaiku:
    def _make_message(self, text: str) -> MagicMock:
        block = MagicMock()
        block.type = "text"
        block.text = text
        msg = MagicMock()
        msg.content = [block]
        return msg

    @patch("haiku.core.anthropic.Anthropic")
    def test_returns_three_line_string(self, mock_cls: MagicMock) -> None:
        poem = "leaf falls from the tree\na function disappears too\nnothing breaks today"
        mock_cls.return_value.messages.create.return_value = self._make_message(poem)
        result = generate_haiku(diff="--- a\n+++ b\n-old\n+new")
        assert len(result.splitlines()) == 3

    @patch("haiku.core.anthropic.Anthropic")
    def test_passes_diff_to_api(self, mock_cls: MagicMock) -> None:
        poem = "one\ntwo\nthree"
        mock_cls.return_value.messages.create.return_value = self._make_message(poem)
        diff = "some diff content"
        generate_haiku(diff=diff)
        call_kwargs = mock_cls.return_value.messages.create.call_args[1]
        user_content = call_kwargs["messages"][0]["content"]
        assert diff in user_content

    @patch("haiku.core.anthropic.Anthropic")
    def test_uses_specified_model(self, mock_cls: MagicMock) -> None:
        poem = "one\ntwo\nthree"
        mock_cls.return_value.messages.create.return_value = self._make_message(poem)
        generate_haiku(diff="x", model="claude-opus-4-6")
        call_kwargs = mock_cls.return_value.messages.create.call_args[1]
        assert call_kwargs["model"] == "claude-opus-4-6"
