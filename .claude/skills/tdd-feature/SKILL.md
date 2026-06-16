---
name: tdd-feature
description: Implement a feature test-first using a red-green-refactor loop wired to this repo's tooling, producing code behind a clean port/interface with hexagonal boundaries. Triggers on "implement", "add a feature", "build the service", "write the endpoint/use case", or after the architect has defined a slice. Use to drive disciplined, verifiable implementation rather than writing code then bolting on tests.
---

# tdd-feature

Implement a vertical slice of behavior test-first, the way a senior engineer would in this codebase.
Tests come **before** the implementation; the design stays hexagonal; the tooling gate must be green
before the slice is "done."

For a substantial implementation, delegate to the **`python-pro`** agent. If the design isn't clear
yet, get a slice from the **`architect`** agent first.

## The loop

Repeat per thin slice of behavior:

### 1. Red — write the failing test first
- Pick the smallest behavior that moves toward the requirement.
- Put the test in `tests/`, mirroring the package path; name it `test_*.py`.
- Test **behavior through the public interface / port**, not internals. Use a fake adapter, not a
  heavy mock, where a port is involved.
- Run it and confirm it fails for the *right reason*:
  ```
  uv run pytest tests/path/test_thing.py::test_case -q
  ```

### 2. Green — simplest code that passes
- Write the minimum to pass. No speculative generality, no config nobody asked for.
- Keep the **domain pure** (no I/O, no framework imports). The domain depends on **ports**
  (`Protocol`s); concrete adapters are injected at the composition root (`app/`).
- Full type hints; mypy runs strict.

### 3. Refactor — clean while green
- Remove duplication, improve names, deepen modules (narrow interface, hidden complexity).
- Tests stay green throughout.

### 4. Verify the gate before declaring done
```
uv run ruff check .
uv run ruff format .
uv run mypy src
uv run pytest
```

Then move to the next slice.

## Conventions (this repo)

- Python **3.12**, full type hints, modern typing (`list[str]`, `X | None`).
- ruff line-length **100**, **double quotes**, rules `E,F,I,UP,B,SIM,N`.
- src-layout: code in `src/mas_global/{domain,ports,adapters,services,app}/`, tests mirror it.
- Always run tools via `uv run` — never bare `python`/`pytest`/`mypy`.

## Done means

A new behavior, covered by a test that was red before it was green, behind a clean interface, with
ruff + mypy strict + pytest all passing. If you can't show the green run, it isn't done.
