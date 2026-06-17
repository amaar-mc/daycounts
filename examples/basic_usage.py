"""
Basic usage examples for daycounts.

Run with:
    python examples/basic_usage.py
"""

from __future__ import annotations

import datetime

from daycounts import (
    Convention,
    accrued_interest,
    actual_360,
    actual_365_fixed,
    actual_actual_isda,
    thirty_360_us,
    thirty_e_360,
    year_fraction,
)

d1 = datetime.date(2024, 1, 1)
d2 = datetime.date(2024, 7, 1)

print("=== Year fractions: 2024-01-01 to 2024-07-01 ===")
print(f"  Actual/360:           {actual_360(d1, d2):.6f}")
print(f"  Actual/365F:          {actual_365_fixed(d1, d2):.6f}")
print(f"  Actual/Actual ISDA:   {actual_actual_isda(d1, d2):.6f}")
print(f"  30/360 US:            {thirty_360_us(d1, d2):.6f}")
print(f"  30E/360:              {thirty_e_360(d1, d2):.6f}")

print()
print("=== Using the dispatcher ===")
for conv in Convention:
    yf = year_fraction(d1, d2, conv)
    print(f"  {conv.value:<25s}  {yf:.6f}")

print()
print("=== Accrued interest ===")
# USD 1,000,000 notional, 5% annual coupon, Actual/360 basis
ai = accrued_interest(
    face=1_000_000.0,
    rate=0.05,
    d1=datetime.date(2024, 1, 1),
    d2=datetime.date(2024, 7, 1),
    convention="actual/360",
)
print(f"  1M * 5% * Act/360 (H1 2024): USD {ai:,.2f}")

print()
print("=== 30/360 US end-of-February edge case ===")
# When D1 and D2 are both the last day of February, the period counts as 1 month.
ai_eom = year_fraction(
    datetime.date(2024, 2, 29),
    datetime.date(2025, 2, 28),
    Convention.THIRTY_360_US,
)
print(f"  2024-02-29 to 2025-02-28 under 30/360 US: {ai_eom:.6f}  (expected 1.0)")
