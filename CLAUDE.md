# CLAUDE.md

This file guides Claude Code (claude.ai/code) when working in this repository.

## Purpose

`mas_global` is an **AI-assisted-development interview harness** for a *Senior Advanced Python
Developer* exercise. The interview does **not** evaluate prompt-writing cleverness — it evaluates
the candidate's ability to **detect an error, correct it, and direct the AI toward a correct,
verified result**. Every part of this harness exists to make that loop fast and visible.

Keep this objective front-of-mind: favor small, verified increments; surface and fix errors
methodically; never claim "done" without a green tooling run.

> Human-facing prep notes live in [`docs/INTERVIEW_GUIDE.md`](docs/INTERVIEW_GUIDE.md).

## Commands

Run everything through `uv` — never bare `python`/`pytest`/`mypy`.

| Action | Command |
|---|---|
| Install / sync deps | `uv sync` |
| Run tests | `uv run pytest` (single: `uv run pytest tests/x.py::test -q`) |
| Lint | `uv run ruff check .` |
| Format | `uv run ruff format .` (CI uses `--check`) |
| Type-check | `uv run mypy src` |
| Pre-commit (all hooks) | `uv run pre-commit run --all-files` |

**The gate** — before declaring any change done, all of these must pass:
`uv run ruff check . && uv run ruff format --check . && uv run mypy src && uv run pytest`.

## Conventions

- **Python 3.12**, full type hints everywhere. **mypy runs `strict`** — no untyped defs, no implicit
  `Any`, no missing returns.
- **ruff:** line-length **100**, **double quotes**, rules `E, F, I, UP, B, SIM, N`. Use modern typing
  (`list[str]`, `X | None`) — `UP` will flag legacy `typing.List` / `Optional`.
- **src-layout:** package at `src/mas_global/`. Tests live in `tests/`, mirroring the package path;
  files named `test_*.py`.
- Prefer `pathlib`, `dataclasses`/`Protocol`, `enum`. Raise specific exceptions; never swallow them.

## Architecture doctrine

Design for a microservice-style codebase using **hexagonal / ports-and-adapters**:

- **Domain is pure** — no I/O, no framework imports. It defines the **ports** (Protocols/ABCs) it
  needs. **Adapters** at the edges implement those ports and depend inward. Dependencies always point
  toward the domain.
- **SOLID, applied not recited** — single responsibility, depend on abstractions (ports) not
  concretions, small client-specific interfaces (ISP), open to extension.
- **Deep modules (Ousterhout)** — narrow interface, complexity hidden behind it. Prefer one clear
  function over many shallow helpers. Information hiding is the goal.
- **TDD by default** — failing test first, simplest green, refactor; the test stays as a guard.
- **Avoid over-engineering** — no speculative abstraction, no generic machinery for a single caller.

Target layout (guidance — create modules as features require them, don't pre-build empty dirs):

```
src/mas_global/
  domain/     # entities, value objects, domain services — pure
  ports/      # Protocols the domain depends on (repositories, gateways, clock)
  adapters/   # concrete implementations of ports (db, http, in-memory fakes)
  services/   # use-case orchestration wiring domain + ports
  app/        # composition root: DI wiring, entrypoints, framework glue
```

## Agent roster

Specialist subagents live in `.claude/agents/`. The **main session is the orchestrator** — it
delegates to these (subagents cannot call other subagents).

| Agent | When to use |
|---|---|
| `architect` | Shape a requirement into a hexagonal design: domain, ports, first TDD slice, trade-offs, what NOT to build. Use first for any non-trivial feature. |
| `python-pro` | Implement a slice test-first; idiomatic typed Python 3.12; verifies the gate before done. |
| `code-reviewer` | Review a diff for correctness, SOLID/coupling, coverage, type-safety, over-engineering. |
| `debugger` | Any failure — traceback, failing test, mypy/ruff error, wrong behavior. Root-cause loop. |
| `orchestrator` | Produce a delegation plan (which agent, what order, acceptance criteria) for a larger task. |

Skills in `.claude/skills/`: **`tdd-feature`** (red→green→refactor implementation loop) and
**`debug-fix`** (systematic error detection & correction). Built-ins also apply: `/code-review`,
`verify`, `run`.

## Orchestration workflow (main session follows this)

```
requirement → architect (design + first slice)
            → tdd-feature / python-pro (implement one thin slice, test-first)
            → run the gate (ruff · mypy · pytest)
            → on failure: debug-fix / debugger (reproduce → root-cause → fix → verify)
            → code-reviewer / /code-review
            → iterate on the next slice
```

Do one slice fully (design → test → code → verify → review) before planning the next. Re-plan after
each slice rather than committing to a long plan up front.

## Interview discipline

- **Verify before claiming done** — paste the green gate output; never assert "this should work."
- **Make the error→diagnosis→fix loop visible** — reproduce, hypothesize, root-cause, minimal fix,
  confirm. This is the behavior being scored.
- **Keep changes small and reviewable.** Read every diff. Reject over-engineering and scope creep.
- **Steer by correcting**, not restarting — point at the specific defect and the fix direction.
