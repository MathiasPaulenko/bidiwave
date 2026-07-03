# Contributing to bidiwave

Thanks for your interest in contributing! This guide covers the basics.

## Setup

```bash
git clone https://github.com/MathiasPaulenko/bidiwave.git
cd bidiwave
pip install -e ".[dev]"
```

## Development workflow

1. Create a branch from `main`:

   ```bash
   git checkout -b feat/my-feature
   ```

2. Make your changes. Follow the existing code style:

   - **Python**: PEP 8, enforced by `ruff`
   - **Types**: full type hints, enforced by `mypy`
   - **Docstrings**: Google style

3. Run checks before committing:

   ```bash
   ruff check bidiwave/ tests/
   mypy bidiwave/
   pytest tests/unit/ -c pyproject.toml -x -q
   ```

4. Write tests for new features. Unit tests go in `tests/unit/`.

5. Commit using [conventional commits](https://www.conventionalcommits.org/):

   ```
   feat: add network cache override
   fix: handle null viewport in set_viewport
   docs: update README with emulation examples
   chore: remove obsolete files
   ```

6. Push and open a pull request.

## Pull request checklist

- [ ] `ruff check` passes
- [ ] `mypy bidiwave/` passes
- [ ] `pytest tests/unit/ -c pyproject.toml` passes
- [ ] New features have unit tests
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## Project structure

```
bidiwave/
├── bidiwave/
│   ├── protocol/      # Pydantic models for commands, events, results
│   ├── transport/     # WebSocket connection, correlator, serializer
│   ├── events/        # Event dispatcher, queue, handlers
│   ├── modules/       # High-level API modules (browsing, script, etc.)
│   ├── convenience/   # Page object, high-level helpers
│   ├── _internal/     # Logging
│   ├── client.py      # BiDiClient — main entry point
│   ├── config.py      # ClientConfig, TransportConfig
│   └── exceptions.py  # Error hierarchy
├── tests/
│   ├── unit/          # Unit tests (no browser needed)
│   └── integration/   # Integration tests (require real browser)
├── docs/              # MkDocs documentation
└── .github/workflows/ # CI/CD pipelines
```

## Reporting bugs

Open an [issue](https://github.com/MathiasPaulenko/bidiwave/issues) with:

- bidiwave version (`pip show bidiwave`)
- Browser and version
- Python version
- Minimal reproduction code
- Error traceback

## License

By contributing, you agree that your contributions are licensed under the MIT
License.
