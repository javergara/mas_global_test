#!/usr/bin/env bash
# Scaffolds a uv-managed, src-layout Python project in the current directory:
# git init, .gitignore, pyproject.toml (ruff/mypy/pytest config), pre-commit
# hooks, tests/, GitHub Actions CI, README/LICENSE, and an initial commit.
# Idempotent: existing files are left untouched on re-run.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ASSETS="$SKILL_DIR/assets"
REPO_ROOT="$(pwd)"
REPO_NAME="$(basename "$REPO_ROOT")"
PKG_NAME="$(echo "$REPO_NAME" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9_]/_/g; s/^([0-9])/_\1/')"

echo "==> Scaffolding Python project '$REPO_NAME' (package: $PKG_NAME)"

# --- Step 1: git init ------------------------------------------------------
if [ ! -d .git ]; then
  git init -b main
else
  echo "git repo already initialized, skipping git init"
fi

if [ ! -f .gitignore ]; then
  cp "$ASSETS/gitignore.template" .gitignore
else
  echo ".gitignore already exists, skipping"
fi

# --- Step 2: uv project init (src layout) -----------------------------------
if [ ! -f pyproject.toml ]; then
  uv init --name "$PKG_NAME" --package --app --vcs none --author-from auto .
else
  echo "pyproject.toml already exists, skipping uv init"
fi

uv add --dev ruff pre-commit mypy pytest
uv sync

# --- Step 3: append tool config sections to pyproject.toml ------------------
NEEDS_APPEND=0
for section in "[tool.ruff]" "[tool.mypy]" "[tool.pytest.ini_options]"; do
  if ! grep -qF "$section" pyproject.toml; then
    NEEDS_APPEND=1
  fi
done
if [ "$NEEDS_APPEND" = "1" ]; then
  printf '\n' >> pyproject.toml
  cat "$ASSETS/pyproject.append.toml" >> pyproject.toml
else
  echo "pyproject.toml already has ruff/mypy/pytest config, skipping append"
fi

# --- Step 4: tests/ directory -----------------------------------------------
mkdir -p tests
if [ ! -f tests/test_placeholder.py ]; then
  cat > tests/test_placeholder.py <<'EOF'
def test_placeholder() -> None:
    """Replace this with real tests as the project grows."""
    assert True
EOF
fi
[ -f tests/__init__.py ] || touch tests/__init__.py

# --- Step 5: pre-commit config + GitHub Actions CI ---------------------------
if [ ! -f .pre-commit-config.yaml ]; then
  RUFF_VERSION="$(uv run ruff --version | awk '{print $2}')"
  MYPY_VERSION="$(uv run mypy --version | awk '{print $2}')"
  sed -e "s/__RUFF_REV__/v${RUFF_VERSION}/" \
      -e "s/__MYPY_REV__/v${MYPY_VERSION}/" \
      "$ASSETS/pre-commit-config.yaml.template" > .pre-commit-config.yaml
else
  echo ".pre-commit-config.yaml already exists, skipping"
fi

mkdir -p .github/workflows
if [ ! -f .github/workflows/ci.yml ]; then
  cp "$ASSETS/ci.yml.template" .github/workflows/ci.yml
else
  echo ".github/workflows/ci.yml already exists, skipping"
fi

uv run pre-commit install

# --- Step 6: README + LICENSE -------------------------------------------------
YEAR="$(date +%Y)"
HOLDER="$(git config user.name 2>/dev/null || true)"
HOLDER="${HOLDER:-$(whoami)}"

if [ ! -f LICENSE ]; then
  sed -e "s/__YEAR__/${YEAR}/" -e "s/__HOLDER__/${HOLDER}/" \
      "$ASSETS/LICENSE.template" > LICENSE
else
  echo "LICENSE already exists, skipping"
fi

if [ ! -f README.md ] || grep -q "Add your description here" README.md 2>/dev/null; then
  sed -e "s/__PROJECT_NAME__/${REPO_NAME}/g" -e "s/__PKG_NAME__/${PKG_NAME}/g" \
      "$ASSETS/README.md.template" > README.md
else
  echo "README.md already exists with custom content, skipping"
fi

# --- Step 7: verification gate ------------------------------------------------
echo "==> Running verification"
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
if ! uv run pre-commit run --all-files; then
  echo "pre-commit made fixes; re-staging and re-running once"
  uv run pre-commit run --all-files
fi

# --- Step 8: initial commit ----------------------------------------------------
git add -A
if git rev-parse HEAD >/dev/null 2>&1; then
  echo "repo already has commits, skipping initial commit (review 'git status' for staged changes)"
else
  git commit -m "chore: scaffold python project structure"
fi

echo "==> Scaffold complete."
