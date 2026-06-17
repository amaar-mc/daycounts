# Contributing

## Setup

```bash
git clone https://github.com/amaar-mc/daycounts
cd daycounts
uv venv .venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Before submitting a PR

```bash
pytest              # all tests must pass
ruff check .        # no lint errors
mypy src            # strict type checking clean
```

## Adding a new convention

1. Add the implementation to `src/daycounts/conventions.py` with a full docstring citing the ISDA section.
2. Add the canonical string to `Convention` in `src/daycounts/dispatcher.py`.
3. Add the dispatch entry to `_DISPATCH`.
4. Export from `src/daycounts/__init__.py` and add to `__all__`.
5. Add golden-value tests with hand-derived arithmetic shown in comments.
6. Update `docs/architecture.md` with the formula and reference.
7. Update `README.md`.

## Conventions for implementations

- Inputs must be `datetime.date`.
- No default parameter values -- all parameters explicit.
- Raise `ValueError` with a descriptive message if `d2 < d1`.
- No `TODO` or `FIXME` comments -- implement it or document why it is deferred.

## Commit style

`type(scope): description` -- e.g. `feat: add actual/365l convention`.

No Co-authored-by trailers.
