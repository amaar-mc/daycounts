# daycounts

<p align="center">
  <img src="assets/logo.png" alt="daycounts logo" width="160">
</p>

**Financial day-count conventions in pure Python with zero dependencies.**

Implements seven conventions, a `year_fraction` dispatcher, and an `accrued_interest` helper.  Requires only the Python standard library (`datetime`).

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
| NL/365 | `Convention.NL_365` | (Actual days - Feb 29 count in period) / 365 |
| Actual/365L | `Convention.ACTUAL_365L` | Actual days / 366 if period or end-year is leap, else / 365 |

See `docs/architecture.md` for exact formulas and ISDA 2006 references.

### NL/365 (Actual/365 No-Leap)

Numerator = actual days between d1 and d2, **minus** the number of February 29
occurrences in the half-open interval [d1, d2).  Denominator = 365.

```
year_fraction = (actual_days - leap_days_in_period) / 365
```

Example: 2020-02-28 to 2020-03-01 -- 2 actual days, 1 Feb 29 in interval,
fraction = (2 - 1) / 365 = 1/365.

For periods containing no Feb 29, NL/365 agrees exactly with Actual/365 Fixed.

### Actual/365L (ISMA-Year)

Numerator = actual days.  Denominator = **366** if either:
- the period [d1, d2) contains a February 29, **or**
- d2 falls in a leap year;

otherwise denominator = **365**.

Rule per ISMA Rule Book (2001) Appendix A; also documented in OpenGamma Strata
as `DayCounts.ACT_365L`.

```
denom = 366 if (isleap(d2.year) or period_contains_feb29) else 365
year_fraction = actual_days / denom
```

Examples:
- 2023-01-01 to 2023-07-01: 181 days, d2 in non-leap 2023, no Feb 29 -- 181/365
- 2023-07-01 to 2024-01-01: 184 days, d2 in leap 2024 -- 184/366
- 2020-01-01 to 2020-07-01: 182 days, Feb 29 2020 in period -- 182/366

## Usage

```python
import datetime
from daycounts import (
    Convention,
    actual_360,
    actual_365_fixed,
    actual_365l,
    actual_actual_isda,
    nl_365,
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
print(nl_365(d1, d2))               # 0.4959...  (181/365, Feb 29 removed)
print(actual_365l(d1, d2))          # 0.4972...  (182/366, 2024 is leap)

# Dispatcher (accepts enum or string)
print(year_fraction(d1, d2, Convention.ACTUAL_360))
print(year_fraction(d1, d2, "actual/360"))
print(year_fraction(d1, d2, Convention.NL_365))
print(year_fraction(d1, d2, "nl/365"))
print(year_fraction(d1, d2, Convention.ACTUAL_365L))
print(year_fraction(d1, d2, "actual/365l"))
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
"nl/365"
"actual/365l"
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
