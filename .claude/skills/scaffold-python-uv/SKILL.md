---
name: scaffold-python-uv
description: This skill should be used when the user asks to "scaffold a python project", "set up this repo", "init python project", "bootstrap with uv", "set up a new python project with uv", "initialize this repository as a python project", or "create the project structure" in a fresh/empty repository. It fully automates git initialization, a uv-managed src-layout Python project, ruff/mypy/pytest tooling, pre-commit hooks, GitHub Actions CI, and README/LICENSE scaffolding, then makes an initial commit.
version: 1.0.0
---

# Scaffold a uv-managed Python project

Turn an empty (or mostly empty) repository into a fully tooled Python project: git
initialized with a sensible `.gitignore`, a `uv`-managed `src/` layout project,
`ruff` (lint + format) and `mypy` enforced via `pre-commit`, a `pytest` test
suite, GitHub Actions CI, README/LICENSE, and an initial commit — in one pass,
without pausing for confirmation between steps.

## When to use

Use this skill when the user wants to bootstrap a brand-new Python project in
the current repository, e.g. "scaffold a python project here", "set up this
repo with uv", "bootstrap this with uv and ruff", "initialize this as a python
project", or similar.

## What it does

Run the orchestration script from the repository root:

```bash
bash .claude/skills/scaffold-python-uv/scripts/scaffold.sh
```

The script performs these stages in order:

1. **Git** — `git init -b main` (skipped if `.git/` already exists) and writes
   a Python `.gitignore`.
2. **uv project init** — `uv init --package --app` to create a `src/<pkg>/`
   layout `pyproject.toml`. The package name is derived from the repo
   directory name (lowercased, non-alphanumerics → `_`). Note: uv normalizes
   the **distribution name** in `[project.name]` to hyphens (e.g. `mas_global`
   → `mas-global`) per PEP 503, while the importable package under `src/` and
   the `tests/` package keep the underscored form — this is expected, not a
   bug.
3. **Dev tooling** — `uv add --dev ruff pre-commit mypy pytest`, then
   `uv sync`. Appends `[tool.ruff]`, `[tool.mypy]`, `[tool.pytest.ini_options]`,
   and a `[[tool.uv.index]]` pin to public PyPI (`default = true`) to
   `pyproject.toml`. Before any resolution, the script unsets
   `UV_INDEX_URL`/`UV_EXTRA_INDEX_URL`/`UV_DEFAULT_INDEX`/`UV_INDEX` for its
   own process tree: a locally configured private index (e.g. a corporate
   Artifactory mirror) gets baked into `uv.lock` as each package's source
   registry, and CI runners won't have credentials for that mirror — causing
   `uv sync --locked` to fail there with a 401. Resolving against public PyPI
   keeps the lockfile usable in CI without secrets.
4. **Tests** — creates `tests/` with a placeholder test wired into pytest via
   `testpaths`.
5. **Pre-commit** — writes `.pre-commit-config.yaml` (ruff lint + format,
   mypy) pinned to the actually-installed tool versions, then runs
   `uv run pre-commit install`. `pre-commit` is a dev dependency only (not on
   PATH), so it must always be invoked via `uv run pre-commit ...`.
6. **CI** — writes `.github/workflows/ci.yml` running ruff, mypy, and pytest
   via `uv` on push/PR.
7. **README + LICENSE** — writes a README with dev-setup/common-task
   instructions and an MIT `LICENSE` (copyright holder from
   `git config user.name`, falling back to the system username).
8. **Verification gate** — runs `ruff check`, `ruff format --check`,
   `mypy src`, `pytest`, and `pre-commit run --all-files` and only proceeds to
   commit if all pass.
9. **Commit** — `git add -A` and commits as `chore: scaffold python project
   structure`, but only if the repo has no prior commits; otherwise leaves
   the changes staged for manual review.

The script uses `set -euo pipefail`, so it stops immediately on the first
failing command rather than continuing into a broken or partial commit.

## Idempotency

Every step checks whether its target file already exists and skips it if so
(an existing `.gitignore`, `.pre-commit-config.yaml`, `ci.yml`, `LICENSE`, or
test file is never overwritten; an existing `README.md` is only replaced if it
still contains uv's generated placeholder text). Re-running the script on an
already-scaffolded repo is safe and a no-op for files that already exist.

## Verification

After running the script, confirm it actually worked:

- `git log --oneline` shows the initial commit and `git status` is clean.
- The script's own verification gate (step 8 above) exited successfully — if
  it didn't, the script would have stopped before committing, so a clean exit
  code is itself proof of a healthy scaffold.
- Spot check `pyproject.toml` for the `src`-layout package name normalization
  and that `requires-python` reflects the Python version pinned in
  `.python-version`.
- Optionally re-run the script once more to confirm it no-ops cleanly on a
  second invocation.

If any individual check fails after the fact, fix the underlying generated
file/config directly and re-run just that one `uv run ...` command rather than
the whole script.
