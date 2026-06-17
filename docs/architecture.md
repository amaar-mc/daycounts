# Architecture

## Module layout

```
src/daycounts/
    __init__.py       -- public API re-exports
    conventions.py    -- five direct day-count functions
    dispatcher.py     -- Convention enum + year_fraction dispatcher
    accrued.py        -- accrued_interest helper
    py.typed          -- PEP 561 marker
```

## Convention definitions

All formulas are from ISDA 2006 Definitions, Section 4.16 (Day Count Fractions).

### Actual/360 -- Section 4.16(e)

    year_fraction = (d2 - d1).days / 360

No adjustment to the numerator or denominator.  A 365-day year yields 365/360 = 1.0138...

### Actual/365 Fixed -- Section 4.16(d)

    year_fraction = (d2 - d1).days / 365

The denominator is always 365, regardless of whether the period spans a leap year.

### Actual/Actual ISDA -- Section 4.16(b)

Split the period at calendar-year boundaries.  For each calendar year Y that overlaps [d1, d2):

    year_fraction += days_in_Y_within_period / (366 if leap(Y) else 365)

For a period that stays within one year Y:

    year_fraction = (d2 - d1).days / (366 if leap(Y) else 365)

This correctly handles multi-year spans by summing contributions from each year.

Example (ISDA 2006 / QuantLib reference):

    d1 = 2003-11-01, d2 = 2004-05-01
    In 2003 (non-leap): Nov(30)+Dec(31) = 61 days  -> 61/365  = 0.167123
    In 2004 (leap):     Jan(31)+Feb(29)+Mar(31)+Apr(30) = 121 days -> 121/366 = 0.330601
    Total = 0.497724

### 30/360 US Bond Basis -- Section 4.16(f)

Let D1, D2 be the day-of-month components of d1 and d2 respectively.

Apply adjustments in order:

1. If D1 is the last day of February AND D2 is the last day of February: set D2 = 30.
2. If D1 is the last day of February: set D1 = 30.
3. If D2 == 31 AND D1 in {30, 31}: set D2 = 30.
4. If D1 == 31: set D1 = 30.

Then:

    year_fraction = ((Y2-Y1)*360 + (M2-M1)*30 + (D2_adj - D1_adj)) / 360

The end-of-February rules (1 and 2) are the defining feature of this convention.
When both endpoints fall on the last day of February, the period is treated as
exactly one calendar month: D1=30, D2=30 means 0 day contribution from the day
component, but M2-M1=1 contributes 30/360 = 1 month.

### 30E/360 Eurobond -- Section 4.16(g)

Simpler than 30/360 US: adjust only for the 31st, never for February.

    If D1 == 31: D1 = 30
    If D2 == 31: D2 = 30

    year_fraction = ((Y2-Y1)*360 + (M2-M1)*30 + (D2_adj - D1_adj)) / 360

Because February is not adjusted, the year fraction from 2024-02-29 to 2025-02-28
is (360 + 0*30 + (28-29)) / 360 = 359/360, not 1.0.

## Dispatcher

`Convention` is a `str`-`Enum` so members double as canonical strings:

    Convention.ACTUAL_360 == 'actual/360'  # True

`year_fraction(d1, d2, convention)` accepts either a `Convention` member or a
plain string (case-insensitive).  Unknown strings raise `ValueError` with the
full list of valid values.

## Error handling

All functions raise `ValueError` if `d2 < d1` or if a convention string is
unrecognized.  No other exceptions are raised under normal usage.

## References

- ISDA 2006 Definitions, Section 4.16 (Day Count Fractions).
- QuantLib reference implementation: `ql/time/daycounters/` (consulted for
  golden test values; QuantLib is not a runtime dependency).
