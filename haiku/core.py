import os
import textwrap
from typing import Optional

from openai import OpenAI

_GROQ_BASE_URL = "https://api.groq.com/openai/v1"
_DEFAULT_MODEL = "llama-3.1-8b-instant"

_SYSTEM_PROMPT = textwrap.dedent(
    """\
    You are a poet who has spent years reading git logs.
    Given a unified diff, you write a single haiku that captures the spirit
    of the change. The haiku must follow the traditional 5-7-5 syllable
    structure across three lines and nothing more.

    Rules:
    - Output exactly three lines, no titles, no labels, no commentary.
    - Do not name functions, variables, or files literally; evoke feeling instead.
    - Prefer concrete imagery over abstractions.
    - Seasonal or natural references are welcome but not mandatory.
    - Never use dashes, em-hyphens, or emoji.
    """
)


def _build_user_prompt(diff: str, commit_message: Optional[str]) -> str:
    """Create the user-facing prompt shown to the model."""
    if commit_message:
        trimmed_message = commit_message.strip()
        return textwrap.dedent(
            f"""\
            Here is the latest commit message and its diff.

            Commit message:
            {trimmed_message}

            Diff:
            {diff}

            Write a single 5-7-5 haiku that reflects the commit and the change.
            """
        ).strip()

    return textwrap.dedent(
        f"""\
        Here is a unified diff from the last change:

        {diff}

        Write a single 5-7-5 haiku that captures the spirit of this change.
        """
    ).strip()


def generate_haiku(
    diff: str,
    model: str = _DEFAULT_MODEL,
    *,
    commit_message: Optional[str] = None,
) -> str:
    """Generate a haiku about a git diff, optionally guided by a commit message."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. "
            "Get a free key at https://console.groq.com and export it in your shell."
        )

    client = OpenAI(api_key=api_key, base_url=_GROQ_BASE_URL)
    user_prompt = _build_user_prompt(diff=diff, commit_message=commit_message)

    response = client.chat.completions.create(
        model=model,
        max_tokens=120,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    raw = _extract_text(response)
    return _clean(raw)


def _extract_text(response: object) -> str:
    try:
        text = response.choices[0].message.content
    except (AttributeError, IndexError) as exc:
        raise ValueError("Unexpected response shape from Groq API") from exc
    if not text:
        raise ValueError("Groq API returned an empty response")
    return text


def _clean(raw: str) -> str:
    lines = [line.strip() for line in raw.strip().splitlines() if line.strip()]
    if len(lines) < 3:
        raise ValueError(
            f"Expected 3 haiku lines, got {len(lines)}. Raw output: {raw!r}"
        )
    return "\n".join(lines[:3])