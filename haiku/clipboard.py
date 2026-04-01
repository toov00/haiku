import shutil
import subprocess
import sys


def copy_text(text: str) -> bool:
    if not text:
        return False
    payload = text if text.endswith("\n") else text + "\n"

    if sys.platform == "darwin":
        return _run_stdin(["pbcopy"], payload)
    if sys.platform == "win32":
        return _copy_windows(payload)

    if shutil.which("wl-copy"):
        return _run_stdin(["wl-copy"], payload)
    if shutil.which("xclip"):
        return _run_stdin(["xclip", "-selection", "clipboard"], payload)
    return False


def _run_stdin(cmd: list[str], payload: str) -> bool:
    try:
        subprocess.run(
            cmd,
            input=payload,
            text=True,
            check=True,
            capture_output=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _copy_windows(payload: str) -> bool:
    try:
        subprocess.run(
            ["clip"],
            input=payload.encode("utf-16-le"),
            check=True,
            capture_output=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False
