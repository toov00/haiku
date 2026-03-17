from haiku.display import _center, _style_line


class TestCenter:
    def test_centers_short_line(self) -> None:
        result = _center("hi", "hi", 20)
        assert result == " " * 9 + "hi"

    def test_no_padding_for_long_line(self) -> None:
        long_line = "x" * 30
        result = _center(long_line, long_line, 20)
        assert result == long_line

    def test_plain_and_displayable_differ(self) -> None:
        plain = "hello"
        displayable = "\033[1mhello\033[0m"
        result = _center(displayable, plain, 20)
        padding = (20 - len(plain)) // 2
        assert result.startswith(" " * padding)
        assert displayable in result


class TestStyleLine:
    def test_no_color_returns_plain(self) -> None:
        assert _style_line("test", index=0, color=False) == "test"

    def test_middle_line_is_dim(self) -> None:
        styled = _style_line("middle", index=1, color=True)
        assert "middle" in styled

    def test_outer_lines_are_bold(self) -> None:
        for i in (0, 2):
            styled = _style_line("line", index=i, color=True)
            assert "line" in styled
