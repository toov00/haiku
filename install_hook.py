import argparse
import os
import stat
import subprocess
import sys
from pathlib import Path


HOOK_BODY = """\
#!/bin/sh
# Added by haiku. Remove with: python install_hook.py --remove
if command -v haiku >/dev/null 2>&1; then
    haiku
fi
"""

HOOK_MARKER = "Added by haiku"


def git_hooks_dir() -> Path:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("error: not inside a git repository", file=sys.stderr)
        sys.exit(1)
    return Path(result.stdout.strip()) / "hooks"


def install(hooks_dir: Path) -> None:
    hook_path = hooks_dir / "post-commit"

    if hook_path.exists():
        existing = hook_path.read_text()
        if HOOK_MARKER in existing:
            print("haiku hook is already installed.")
            return
        updated = existing.rstrip("\n") + "\n\n" + HOOK_BODY.lstrip("\n")
        hook_path.write_text(updated)
    else:
        hook_path.write_text("#!/bin/sh\n" + HOOK_BODY)

    current = stat.S_IMODE(hook_path.stat().st_mode)
    hook_path.chmod(current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"installed post-commit hook at {hook_path}")


def remove(hooks_dir: Path) -> None:
    hook_path = hooks_dir / "post-commit"

    if not hook_path.exists():
        print("no post-commit hook found.")
        return

    text = hook_path.read_text()
    if HOOK_MARKER not in text:
        print("haiku hook not present in post-commit hook.")
        return

    lines = text.splitlines(keepends=True)
    cleaned = [
        line for line in lines
        if HOOK_MARKER not in line and "haiku" not in line
    ]
    result = "".join(cleaned).rstrip("\n") + "\n"

    if result.strip() in ("", "#!/bin/sh"):
        hook_path.unlink()
        print(f"removed {hook_path}")
    else:
        hook_path.write_text(result)
        print(f"removed haiku lines from {hook_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--remove",
        action="store_true",
        help="Remove the hook instead of installing it.",
    )
    args = parser.parse_args()

    hooks_dir = git_hooks_dir()

    if args.remove:
        remove(hooks_dir)
    else:
        install(hooks_dir)


if __name__ == "__main__":
    main()
