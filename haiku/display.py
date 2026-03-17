import shutil

import click


_MAX_CENTER_WIDTH = 80


def print_haiku(poem: str, color: bool = True) -> None:
    lines = poem.splitlines()
    if not lines:
        return

    terminal_width = min(shutil.get_terminal_size(fallback=(80, 24)).columns, _MAX_CENTER_WIDTH)

    longest_line = max(len(line) for line in lines)
    inner_width = max(0, min(_MAX_CENTER_WIDTH, longest_line + 4))
    margin = max(0, (terminal_width - inner_width) // 2)

    if inner_width <= 2:
        raw_border = "=" * inner_width
    else:
        chars = ["="] * inner_width
        mid = inner_width // 2
        chars[mid] = "*"
        raw_border = "".join(chars)

    border = " " * margin + click.style(raw_border, dim=True) if color else " " * margin + raw_border

    click.echo("")
    click.echo(border)

    for i, line in enumerate(lines):
        styled = _style_line(line, index=i, color=color)
        padded = _center(styled if color else line, line, inner_width)
        click.echo(" " * margin + padded)

    click.echo(border)
    click.echo("")


def _style_line(line: str, index: int, color: bool) -> str:
    if not color:
        return line

    if index == 1:
        return click.style(line, dim=True)
    return click.style(line, bold=True)


def _center(displayable: str, plain: str, width: int) -> str:
    padding = max(0, (width - len(plain)) // 2)
    return " " * padding + displayable
