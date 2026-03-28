
import os
from unittest.mock import MagicMock, patch

import pytest

from haiku.core import generate_haiku, _clean, _DEFAULT_MODEL


def _make_response(text: str) -> MagicMock:
    message = MagicMock()
    message.content = text
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    return response


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
    @patch.dict(os.environ, {"GROQ_API_KEY": "test-key"})
    @patch("haiku.core.OpenAI")
    def test_returns_three_line_string(self, mock_cls: MagicMock) -> None:
        poem = "leaf falls from the tree\na function disappears too\nnothing breaks today"
        mock_cls.return_value.chat.completions.create.return_value = _make_response(poem)
        result = generate_haiku(diff="--- a\n+++ b\n-old\n+new")
        assert len(result.splitlines()) == 3

    @patch.dict(os.environ, {"GROQ_API_KEY": "test-key"})
    @patch("haiku.core.OpenAI")
    def test_passes_diff_to_api(self, mock_cls: MagicMock) -> None:
        poem = "one\ntwo\nthree"
        mock_cls.return_value.chat.completions.create.return_value = _make_response(poem)
        diff = "some diff content"
        generate_haiku(diff=diff)
        call_kwargs = mock_cls.return_value.chat.completions.create.call_args[1]
        user_message = call_kwargs["messages"][1]["content"]
        assert diff in user_message

    @patch.dict(os.environ, {"GROQ_API_KEY": "test-key"})
    @patch("haiku.core.OpenAI")
    def test_uses_specified_model(self, mock_cls: MagicMock) -> None:
        poem = "one\ntwo\nthree"
        mock_cls.return_value.chat.completions.create.return_value = _make_response(poem)
        generate_haiku(diff="x", model="llama-3.3-70b-versatile")
        call_kwargs = mock_cls.return_value.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == "llama-3.3-70b-versatile"

    @patch.dict(os.environ, {"GROQ_API_KEY": "test-key"})
    @patch("haiku.core.OpenAI")
    def test_uses_default_model(self, mock_cls: MagicMock) -> None:
        poem = "one\ntwo\nthree"
        mock_cls.return_value.chat.completions.create.return_value = _make_response(poem)
        generate_haiku(diff="x")
        call_kwargs = mock_cls.return_value.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == _DEFAULT_MODEL

    @patch.dict(os.environ, {}, clear=True)
    def test_raises_when_key_missing(self) -> None:
        os.environ.pop("GROQ_API_KEY", None)
        with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
            generate_haiku(diff="x")