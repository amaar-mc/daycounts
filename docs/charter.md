# Project Charter

## Purpose

daycounts provides a minimal, zero-dependency Python library for computing
financial day-count fractions and accrued interest.  It targets quant
developers, fixed-income practitioners, and anyone who needs correct
ISDA-compliant day-count logic without pulling in a heavy scientific stack.

## Scope

In scope:

- Five ISDA 2006 day-count conventions: Actual/360, Actual/365 Fixed,
  Actual/Actual ISDA, 30/360 US Bond Basis, 30E/360 Eurobond.
- A `year_fraction` dispatcher accepting a Convention enum or string.
- An `accrued_interest(face, rate, d1, d2, convention)` helper.
- Strict typing (mypy strict), Python 3.10+, zero runtime dependencies.

Out of scope:

- Schedule generation (coupon dates, business day adjustment).
- Yield / price / duration calculations.
- Additional conventions (e.g. Actual/365L, NL/365, Business/252).
- Currency or unit handling.

## Design principles

- Zero runtime dependencies (standard library `datetime` only).
- Inputs are `datetime.date`; all parameters explicit, no defaults.
- Raise `ValueError` with clear messages on invalid input.
- Strict typing throughout.
- Tested against ISDA 2006 and QuantLib golden values.
