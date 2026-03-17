## haiku

Generates a haiku about your last git diff. Useless and perfect :-)

```text
old function removed
three lines of silence remain
the tests still pass though
```

## What It Does

On each run, `haiku` looks at a git diff (either the last commit or your staged changes), sends it to the Groq API with a tight 5-7-5 prompt, and prints a tiny poem in your terminal. You can run it manually, or wire it up as a post-commit hook so every commit gets its own verse. The haiku is based on the diff itself, and when run after a commit it can also take the commit message into account so the poem feels closer to what you meant to do.

## Installation

Need Python 3.10+ and a free Groq API key (no credit card) from `https://console.groq.com`.

```bash
pip install .
export GROQ_API_KEY="gsk_..."
```

To wire it up as a git hook so the poem appears after every commit:

```bash
python install_hook.py
```

To remove the hook later:

```bash
python install_hook.py --remove
```

For development installs:

```bash
pip install -e ".[dev]"
pytest
```

## Usage

Basic usage:

```bash
haiku
```

Use the staged diff before you commit (nice for previewing):

```bash
haiku --staged
```

Full CLI help:

```text
haiku [OPTIONS]

Options:
  --staged        Use the staged diff instead of the last commit.
  --model TEXT    Groq model to use.  [default: llama-3.1-8b-instant]
  --no-color      Disable colored output.
  --help          Show this message and exit.
```

## How It Works

1. Runs `git diff HEAD~1 HEAD` (or `git diff --cached` with `--staged`).
2. Sends the diff (and, when available, the latest commit message) to the Groq API with a short prompt asking for a single 5-7-5 haiku.
3. Cleans the model output down to exactly three non-empty lines and prints them centered in your terminal.

Diffs larger than 8 KB are trimmed before being sent so you stay well within token limits. Groq's free tier is generous enough that a haiku tool will never come close to hitting it.

## Reference

- Reads diffs from your local git repo; no remote calls except to Groq.
- Uses the `GROQ_API_KEY` environment variable for authentication.
- The default model is `llama-3.1-8b-instant`, but you can override it with `--model` at the CLI.
- `install_hook.py` adds or removes a simple `post-commit` hook that calls `haiku` after each commit.

## Limitations

- Requires a git repository; outside a repo it will fail with a git error.
- Very large diffs are truncated, which means the poem may only reflect part of the change.
- Needs network access to reach Groq's API.

## Contributing

Issues and PRs are very welcome!

## License

MIT
