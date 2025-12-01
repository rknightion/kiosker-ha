---
title: Development
description: Set up a local development environment for the Kiosker Home Assistant integration, run tests, and preview docs.
---

# Development

This project uses [uv](https://github.com/astral-sh/uv) for Python dependency management and targets modern Home Assistant versions.

## Prerequisites

- Python 3.11+ (managed by `uv` during setup)
- `uv` installed (`pip install uv` if you do not have it yet)
- Home Assistant core development dependencies (installed via `make install`)

## Setup

```bash
make install
```

This syncs all dev dependencies using `uv`.

## Common tasks

| Task | Command |
| ---- | ------- |
| Format code | `make format` |
| Lint (ruff, mypy, bandit) | `make lint` |
| Run tests | `make test` |
| Start HA dev instance | `make develop` |
| Clean caches | `make clean` |

### Running Home Assistant for local testing

`make develop` launches Home Assistant with the repository as `custom_components` and stores configuration under `./config`. A minimal `secrets.yaml` is created if missing. Access the UI at `http://localhost:8123`.

### Debug logging

Enable verbose logging while developing:

```yaml
logger:
  default: info
  logs:
    custom_components.kiosker: debug
    aiohttp: warning
```

## Documentation

Docs live under `docs/` and are built with MkDocs Material. To preview locally:

```bash
uv run mkdocs serve
```

The site URL and deployment are managed separately in the `m7kni-net-site` repo; this project just provides the sources.

## Pull request checklist

- [ ] New/changed entities documented under `docs/`
- [ ] `make lint` and `make test` pass
- [ ] New services or options have translations and `services.yaml` entries
- [ ] Add or update tests where appropriate
