---
name: debug-fix
description: Systematic error detection and correction for Python. Use this when a test is failing, a traceback or exception appears, mypy/ruff reports an error, or runtime behavior is wrong. Triggers on "fix this error", "tests are failing", "debug this", "why does this break", or when a traceback/stack trace is pasted. Drives a reproduce → isolate → root-cause → failing-test → minimal-fix → verify loop rather than guessing.
---

# debug-fix

A disciplined procedure for finding and fixing the **root cause** of a failure — the core skill this
repo's interview harness is built around. The goal is never "make the red go away"; it is to
understand *why* it broke, prove it with a test, and stop it from returning.

For a deep, multi-step investigation, delegate to the **`debugger`** agent. For a quick in-line fix,
follow the steps below directly.

## Procedure

1. **Capture the failure exactly.** Read the *whole* traceback or error. Quote it. Note the mypy
   error code (`[arg-type]`, `[union-attr]`, `[return-value]`, ...) or the ruff rule (`B…`, `SIM…`).
   Do not edit anything yet — premature edits destroy evidence.

2. **Reproduce deterministically.** Reduce to the smallest command that fails:
   `uv run pytest path/to/test.py::test_name -q`. If the bug has no test, **write a failing test
   that reproduces it** before fixing — this is both the repro and the regression guard.

3. **Isolate and hypothesize.** Read the failing code and its callers. State one explicit hypothesis
   ("the value is `None` here because the adapter returns `None` on a cache miss"). Confirm or kill it
   with a targeted inspection (a temporary assert/print, or reading the data flow) — not by editing.

4. **Find the root cause.** Trace from symptom to cause. The bottom frame of a traceback is usually
   where it *surfaced*, not where the wrong value was *created*. Explain the cause in terms of the
   code's logic.

5. **Apply the minimal fix.** Change the least code that addresses the cause. Don't refactor or
   reformat unrelated lines in the same pass — keep the diff small and reviewable. If the fix exposes
   a design flaw, note it separately rather than fixing it silently.

6. **Verify green.** Confirm the repro test now passes and nothing regressed:
   ```
   uv run ruff check .
   uv run mypy src
   uv run pytest
   ```

7. **Leave it defended.** Keep the reproducing test in the suite. Briefly state the root cause and
   the fix.

## Reading Python failures fast

- **Traceback:** bottom = the exception type/message; read upward to find where the bad input
  originated.
- **mypy strict:** the error code names the category. A `None` flowing through `X | None` is the
  classic — handle the `None` branch; do not silence it with `cast` or `# type: ignore`.
- **ruff `B`/`SIM`:** often real latent bugs (mutable default args, unreachable branches), not style.

## Anti-patterns to avoid

- Changing code before reproducing the failure.
- Multiple speculative edits at once ("maybe this?") — one hypothesis at a time.
- Declaring it fixed without running the full gate.
- Deleting/loosening the test to make it pass.
- Catching and swallowing the exception instead of fixing the cause.
