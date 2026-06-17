# daycounts

Pure-Python financial day-count conventions library. Zero runtime dependencies.

## Stack

- Python 3.10+, uv, hatchling
- pytest for tests
- ruff for lint (line-length=100)
- mypy strict

## Commands

```bash
uv pip install -e ".[dev]"
pytest -q
ruff check .
mypy src
uv build
uv run --with twine twine check dist/*
```

## Layout

```
src/daycounts/
    __init__.py       -- public API surface
    conventions.py    -- five direct day-count functions
    dispatcher.py     -- Convention enum + year_fraction
    accrued.py        -- accrued_interest helper
    py.typed          -- PEP 561 marker
tests/                -- pytest tests (golden values + properties)
examples/             -- usage scripts
docs/                 -- architecture.md and charter.md
assets/               -- placeholder for logo etc.
```

## Conventions

- All functions: raise ValueError if d2 < d1.
- No default parameter values; all params explicit.
- Inputs are datetime.date only.
- From __future__ import annotations in every module.
- Commits: type(scope): description
- No Co-authored-by trailers.

## Convention string values (canonical, case-insensitive)

- actual/360
- actual/365f
- actual/actual isda
- 30/360 us
- 30e/360
