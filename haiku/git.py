import subprocess
from dataclasses import dataclass


class GitError(RuntimeError):
    """."""

@dataclass(frozen=True)
class DiffOptions:
    staged: bool = False
    max_bytes: int = 8_000


def get_last_diff(staged: bool = False, max_bytes: int = 8_000) -> str:
    options = DiffOptions(staged=staged, max_bytes=max_bytes)
    return _run_diff(options)


def get_last_commit_message() -> str:
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError as exc:
        raise GitError("git executable not found on PATH") from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip()
        raise GitError(stderr or f"git exited with status {exc.returncode}") from exc

    return result.stdout.strip()


def _run_diff(options: DiffOptions) -> str:
    if options.staged:
        cmd = ["git", "diff", "--cached"]
    else:
        cmd = ["git", "diff", "HEAD~1", "HEAD"]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError as exc:
        raise GitError("git executable not found on PATH") from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip()
        raise GitError(stderr or f"git exited with status {exc.returncode}") from exc

    diff = result.stdout
    return _maybe_truncate(diff, options.max_bytes)


def _maybe_truncate(diff: str, max_bytes: int) -> str:
    encoded = diff.encode()
    if len(encoded) <= max_bytes:
        return diff

    truncated = encoded[:max_bytes].decode(errors="ignore")
    return truncated + "\n\n[diff truncated for brevity]"
