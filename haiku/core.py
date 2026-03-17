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
    - Never use dashes, em-hyphens, or emoji.
    """
)


def _build_user_prompt(diff: str, commit_message: Optional[str]) -> str:
    tone_hint = _infer_tone(diff=diff, commit_message=commit_message)

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
            {tone_hint}
            """
        ).strip()

    return textwrap.dedent(
        f"""\
        Here is a unified diff from the last change:

        {diff}

        Write a single 5-7-5 haiku that captures the spirit of this change.
        {tone_hint}
        """
    ).strip()


def _infer_tone(diff: str, commit_message: Optional[str]) -> str:
    message = (commit_message or "").lower()
    lines = diff.splitlines()

    added = 0
    removed = 0
    for line in lines:
        if line.startswith("---") or line.startswith("+++"):
            continue
        if line.startswith("+"):
            added += 1
        elif line.startswith("-"):
            removed += 1

    total_changed = added + removed
    diff_length = len(diff)

    if message.startswith("merge ") or " merge " in message or "merged branch" in message:
        return (
            "Let the mood feel like rivers joining or branches weaving back together."
        )

    if removed >= 50 and removed > added * 2:
        return "Lean into a quiet, slightly mournful tone for all that was removed."

    if total_changed > 0 and total_changed <= 3 and diff_length < 400:
        return (
            "Keep the tone dry and a little deadpan, as if noting a tiny, precise fix."
        )

    return ""


def generate_haiku(
    diff: str,
    model: str = _DEFAULT_MODEL,
    *,
    commit_message: Optional[str] = None,
) -> str:
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