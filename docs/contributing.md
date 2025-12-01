---
title: Contributing
description: Guidelines for contributing to the Kiosker integration, from filing issues to opening pull requests.
---

# Contributing

Contributions are welcome! Please follow these guidelines to keep the project consistent and easy to maintain.

## Ways to contribute

- Report bugs or request features via [GitHub issues](https://github.com/rknightion/kiosker-ha/issues).
- Improve documentation (typos, clarity, examples).
- Add tests or extend entity coverage for new Kiosker API fields.

## Pull requests

1. Fork the repo and create a feature branch.
2. Run `make format && make lint && make test` locally.
3. Add or update documentation under `docs/` for user-facing changes.
4. Keep changes scoped and descriptive; prefer smaller PRs.
5. Reference related issues in the PR description.

## Coding standards

- Ruff for linting/formatting; follow the existing style.
- Type hints are required; keep mypy happy.
- Avoid breaking changes to entity names/unique IDs unless justified and documented.

## Security and secrets

- Do not commit real access tokens, device URLs, or personal data.
- Use placeholders in examples.

## Release notes

We use release-please for release notes so please make sure your commits align so they're processed automatically.
