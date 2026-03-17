"""Rendering helpers for printing the haiku to the terminal."""

import shutil

import click


_MAX_CENTER_WIDTH = 80


def print_haiku(poem: str, color: bool = True) -> None:
    lines = poem.splitlines()
    terminal_width = min(shutil.get_terminal_size(fallback=(80, 24)).columns, _MAX_CENTER_WIDTH)

    click.echo("")
    for i, line in enumerate(lines):
        styled = _style_line(line, index=i, color=color)
        padded = _center(styled if color else line, line, terminal_width)
        click.echo(padded)
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
