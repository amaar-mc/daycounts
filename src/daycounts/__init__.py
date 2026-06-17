"""
daycounts -- Financial day-count conventions in pure Python.

Zero runtime dependencies.  All functions accept datetime.date objects.

Conventions
-----------
- actual_360: Actual/360
- actual_365_fixed: Actual/365 Fixed
- actual_actual_isda: Actual/Actual ISDA
- thirty_360_us: 30/360 US Bond Basis
- thirty_e_360: 30E/360 Eurobond

Dispatcher
----------
- Convention: str-enum of canonical convention names
- year_fraction: dispatch by Convention or string

Helper
------
- accrued_interest: face * rate * year_fraction
"""

from __future__ import annotations

from daycounts.accrued import accrued_interest
from daycounts.conventions import (
    actual_360,
    actual_365_fixed,
    actual_actual_isda,
    thirty_360_us,
    thirty_e_360,
)
from daycounts.dispatcher import Convention, year_fraction

__all__ = [
    "Convention",
    "accrued_interest",
    "actual_360",
    "actual_365_fixed",
    "actual_actual_isda",
    "thirty_360_us",
    "thirty_e_360",
    "year_fraction",
]

__version__ = "0.1.0"
