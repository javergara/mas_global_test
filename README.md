# mas_global

An **AI-assisted-development interview harness** for a *Senior Advanced Python Developer* exercise.

The interview evaluates not prompt-writing cleverness but the ability to **detect an error, correct
it, and direct the AI toward a correct, verified result**. This repo packages the agents, skills,
and conventions that make that loop fast and visible.

## What's here

- **[`CLAUDE.md`](CLAUDE.md)** — the operating manual: commands, conventions, architecture doctrine
  (hexagonal / SOLID / deep modules / TDD), the agent roster, and the orchestration workflow.
- **[`docs/INTERVIEW_GUIDE.md`](docs/INTERVIEW_GUIDE.md)** — human prep notes: what's being scored,
  the live loop, the error-detection/correction playbook, and a dry-run script.
- **`.claude/agents/`** — specialist subagents: `architect`, `python-pro`, `code-reviewer`,
  `debugger`, `orchestrator`.
- **`.claude/skills/`** — `tdd-feature` (red→green→refactor) and `debug-fix` (root-cause debugging).

## Quickstart

```bash
uv sync                 # install dependencies
uv run pytest           # run tests
uv run ruff check .     # lint
uv run mypy src         # type-check (strict)
```

The full gate (run before declaring any change done):

```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy src && uv run pytest
```

## How to use the harness

Drive the workflow described in `CLAUDE.md`: shape a requirement with the `architect`, implement a
thin slice test-first via `tdd-feature` / `python-pro`, run the gate, and when anything breaks reach
for `debug-fix` / the `debugger` to find the root cause — then review and iterate. Start with the
[interview guide](docs/INTERVIEW_GUIDE.md).
