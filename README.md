# daycounts

**Financial day-count conventions in pure Python with zero dependencies.**

Implements five ISDA-defined conventions, a `year_fraction` dispatcher, and an `accrued_interest` helper.  Requires only the Python standard library (`datetime`).

```
pip install daycounts
```

## Conventions

| Convention | Enum | Description |
|---|---|---|
| Actual/360 | `Convention.ACTUAL_360` | Actual days / 360 |
| Actual/365 Fixed | `Convention.ACTUAL_365_FIXED` | Actual days / 365 |
| Actual/Actual ISDA | `Convention.ACTUAL_ACTUAL_ISDA` | Split by calendar year; leap/non-leap denominators |
| 30/360 US Bond Basis | `Convention.THIRTY_360_US` | 30-day months, 360-day year; EOM February rules apply |
| 30E/360 Eurobond | `Convention.THIRTY_E_360` | 30-day months, 360-day year; no February adjustment |

See `docs/architecture.md` for exact formulas and ISDA 2006 references.

## Usage

```python
import datetime
from daycounts import (
    Convention,
    actual_360,
    actual_365_fixed,
    actual_actual_isda,
    thirty_360_us,
    thirty_e_360,
    year_fraction,
    accrued_interest,
)

d1 = datetime.date(2024, 1, 1)
d2 = datetime.date(2024, 7, 1)

# Direct functions
print(actual_360(d1, d2))           # 0.5055...  (182/360)
print(actual_365_fixed(d1, d2))     # 0.4986...  (182/365)
print(actual_actual_isda(d1, d2))   # 0.4972...  (182/366, all in leap 2024)
print(thirty_360_us(d1, d2))        # 0.5000     (180/360)
print(thirty_e_360(d1, d2))         # 0.5000     (180/360)

# Dispatcher (accepts enum or string)
print(year_fraction(d1, d2, Convention.ACTUAL_360))
print(year_fraction(d1, d2, "actual/360"))
```

### Accrued interest

```python
# USD 1,000,000 notional, 5% annual coupon, Actual/360
ai = accrued_interest(
    face=1_000_000,
    rate=0.05,
    d1=datetime.date(2024, 1, 1),
    d2=datetime.date(2024, 7, 1),
    convention="actual/360",
)
# -> 25277.78
```

### Convention string values

```python
# Canonical strings (case-insensitive):
"actual/360"
"actual/365f"
"actual/actual isda"
"30/360 us"
"30e/360"
```

## Install

```bash
pip install daycounts
uv add daycounts
```

Requires Python 3.10+. Zero runtime dependencies.

PyPI publication is pending (new-project rate limit); install from source in the meantime:

```bash
pip install git+https://github.com/amaar-mc/daycounts.git
```

## Development

```bash
git clone https://github.com/amaar-mc/daycounts
cd daycounts
uv venv .venv && source .venv/bin/activate
uv pip install -e ".[dev]"
pytest -q
ruff check .
mypy src
```

## vs yearfrac / QuantLib

- **yearfrac** (Excel-compatible): supports ~4 conventions, no Actual/Actual ISDA split-year logic.
- **QuantLib / financepy / rateslib**: correct and comprehensive, but pull in large scientific-stack dependencies (NumPy, Cython, or C++ extensions).
- **daycounts**: zero-dependency pip package focused on the five most common ISDA conventions, with strict typing and a clean pure-Python API.

## License

MIT. Copyright (c) 2026 Amaar Chughtai.
