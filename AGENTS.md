# Repository Guidelines

## Project Structure & Module Organization
- `custom_components/kiosker/` holds the Home Assistant integration code (entities, config flow, API client, coordinator, services, translations).
- `tests/` contains the pytest suite (`test_*.py`) plus shared fixtures in `conftest.py`.
- `docs/` is the MkDocs site content; static assets live in `docs/assets/`.
- `scripts/` contains developer helpers; `config/` is a local Home Assistant config folder used for dev runs.

## Build, Test, and Development Commands
- `make install`: install dev dependencies via `uv sync --frozen --dev`.
- `make format`: format Python with Ruff.
- `make lint`: run Ruff checks, mypy, and Bandit.
- `make test`: run pytest with coverage for `custom_components.kiosker`.
- `make develop`: start Home Assistant in dev mode at `http://localhost:8123` using `config/`.
- `make clean`: remove local caches and coverage output.

## Coding Style & Naming Conventions
- Python 3.13, 4-space indentation, line length 88.
- Ruff formatting uses double quotes; keep imports sorted.
- Add type hints for new code and keep mypy passing.
- Follow Home Assistant conventions for entity/platform modules and shared constants (see `const.py`).

## Testing Guidelines
- Add tests under `tests/` with `test_*.py` naming.
- Use pytest markers (`unit`, `integration`, `slow`) when helpful; example: `uv run pytest -m unit`.
- Coverage is configured in `pyproject.toml` and enforced by pytest settings.

## Commit & Pull Request Guidelines
- Commit messages follow Conventional Commits (e.g., `feat: add X`, `fix(api): handle Y`) to support release-please.
- Keep PRs small and focused, include a clear description, and reference related issues.
- For user-facing changes, update docs in `docs/`.
- Run `make format && make lint && make test` before opening a PR.

## Security & Configuration Tips
- Never commit real access tokens, device URLs, or personal data; use placeholders.
- Local secrets belong in `config/secrets.yaml` (created by `make develop`).
