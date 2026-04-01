
import sys

import click

from .clipboard import copy_text
from .core import generate_haiku, _DEFAULT_MODEL
from .git import get_last_diff, get_last_commit_message, GitError
from .display import print_haiku


@click.command()
@click.option(
    "--staged",
    is_flag=True,
    default=False,
    help="Use the staged diff instead of the last commit.",
)
@click.option(
    "--model",
    default=_DEFAULT_MODEL,
    show_default=True,
    help="Model to use for generation (Groq).",
)
@click.option(
    "--no-color",
    is_flag=True,
    default=False,
    help="Disable colored output.",
)
@click.option(
    "--copy",
    "do_copy",
    is_flag=True,
    default=False,
    help="Also copy the haiku to the clipboard (pbcopy, xclip, wl-copy, or Windows clip).",
)
def main(staged: bool, model: str, no_color: bool, do_copy: bool) -> None:
    try:
        diff = get_last_diff(staged=staged)
        commit_message = None if staged else get_last_commit_message()
    except GitError as exc:
        click.echo(f"git: {exc}", err=True)
        sys.exit(1)

    if not diff.strip():
        click.echo("Nothing to write about. The diff is empty.", err=True)
        sys.exit(1)

    try:
        poem = generate_haiku(diff=diff, model=model, commit_message=commit_message)
    except RuntimeError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
    except Exception as exc:
        click.echo(f"generation failed: {exc}", err=True)
        sys.exit(1)

    print_haiku(poem, color=not no_color)

    if do_copy:
        if copy_text(poem):
            click.echo("Copied haiku to clipboard.", err=True)
        else:
            click.echo(
                "Could not copy to clipboard. Install pbcopy (macOS), xclip or wl-copy "
                "(Linux), or use Windows with clip in PATH.",
                err=True,
            )