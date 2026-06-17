"""
Financial day-count convention implementations.

Each function accepts two datetime.date objects d1 (start, inclusive) and
d2 (end, exclusive) and returns a float year fraction according to the
convention defined in ISDA 2006 Definitions, Section 4.16.

References
----------
ISDA 2006 Definitions, Section 4.16 (Day Count Fractions).
"""

from __future__ import annotations

import calendar
import datetime


def _validate(d1: datetime.date, d2: datetime.date) -> None:
    if d2 < d1:
        raise ValueError(f"d2 ({d2}) must not be earlier than d1 ({d1})")


def _is_last_day_of_february(d: datetime.date) -> bool:
    """Return True if d is the last calendar day of February in its year."""
    return d.month == 2 and d.day == calendar.monthrange(d.year, 2)[1]


# ---------------------------------------------------------------------------
# Actual/360  (ISDA 2006 Section 4.16(e))
# ---------------------------------------------------------------------------


def actual_360(d1: datetime.date, d2: datetime.date) -> float:
    """Return the Actual/360 year fraction.

    Year fraction = (d2 - d1).days / 360

    Parameters
    ----------
    d1:
        Start date (period start, inclusive).
    d2:
        End date (period end, exclusive / accrual end).

    Raises
    ------
    ValueError
        If d2 < d1.
    """
    _validate(d1, d2)
    return (d2 - d1).days / 360.0


# ---------------------------------------------------------------------------
# Actual/365 Fixed  (ISDA 2006 Section 4.16(d))
# ---------------------------------------------------------------------------


def actual_365_fixed(d1: datetime.date, d2: datetime.date) -> float:
    """Return the Actual/365 Fixed year fraction.

    Year fraction = (d2 - d1).days / 365

    Parameters
    ----------
    d1:
        Start date (inclusive).
    d2:
        End date (exclusive).

    Raises
    ------
    ValueError
        If d2 < d1.
    """
    _validate(d1, d2)
    return (d2 - d1).days / 365.0


# ---------------------------------------------------------------------------
# Actual/Actual ISDA  (ISDA 2006 Section 4.16(b))
# ---------------------------------------------------------------------------


def actual_actual_isda(d1: datetime.date, d2: datetime.date) -> float:
    """Return the Actual/Actual ISDA year fraction.

    Splits the period at calendar-year boundaries.  For the portion of
    the period that falls in a leap year, the day count is divided by 366;
    for the portion in a non-leap year it is divided by 365.

    Concretely, for each year Y that overlaps [d1, d2):

        contribution = days_in_Y_within_period / (366 if leap else 365)

    Parameters
    ----------
    d1:
        Start date (inclusive).
    d2:
        End date (exclusive).

    Raises
    ------
    ValueError
        If d2 < d1.
    """
    _validate(d1, d2)
    if d1 == d2:
        return 0.0

    total: float = 0.0
    year = d1.year

    while year <= d2.year:
        year_start = max(d1, datetime.date(year, 1, 1))
        year_end = min(d2, datetime.date(year + 1, 1, 1))

        if year_end <= year_start:
            year += 1
            continue

        days_in_year = 366 if calendar.isleap(year) else 365
        total += (year_end - year_start).days / days_in_year
        year += 1

    return total


# ---------------------------------------------------------------------------
# 30/360 US (Bond Basis)  (ISDA 2006 Section 4.16(f))
# ---------------------------------------------------------------------------


def thirty_360_us(d1: datetime.date, d2: datetime.date) -> float:
    """Return the 30/360 US Bond Basis year fraction.

    Adjustment rules (applied in order):

    1. If D1 is the last day of February **and** D2 is the last day of
       February, set D2 = 30.
    2. If D1 is the last day of February, set D1 = 30.
    3. If D2 == 31 and D1 in {30, 31}, set D2 = 30.
    4. If D1 == 31, set D1 = 30.

    Year fraction = ((Y2 - Y1)*360 + (M2 - M1)*30 + (D2_adj - D1_adj)) / 360

    Parameters
    ----------
    d1:
        Start date (inclusive).
    d2:
        End date (exclusive).

    Raises
    ------
    ValueError
        If d2 < d1.

    Notes
    -----
    The end-of-February rule (steps 1 and 2) is the key difference between
    this convention and 30E/360.  When both dates fall on the last day of
    February, the period is treated as exactly one month (D1=30, D2=30 ->
    30 - 30 = 0 day contribution, one month contributed by M2-M1=1).
    When only D1 is end-of-February, D1 is bumped to 30 so that the period
    does not artificially shorten.
    """
    _validate(d1, d2)

    y1, m1, dd1 = d1.year, d1.month, d1.day
    y2, m2, dd2 = d2.year, d2.month, d2.day

    # Step 1: both on last day of February
    if _is_last_day_of_february(d1) and _is_last_day_of_february(d2):
        dd2 = 30
    # Step 2: D1 on last day of February (applied after step 1 may have set dd2)
    if _is_last_day_of_february(d1):
        dd1 = 30
    # Step 3: D2 == 31 and D1 in {30, 31}
    if dd2 == 31 and dd1 in (30, 31):
        dd2 = 30
    # Step 4: D1 == 31
    if dd1 == 31:
        dd1 = 30

    numerator = (y2 - y1) * 360 + (m2 - m1) * 30 + (dd2 - dd1)
    return numerator / 360.0


# ---------------------------------------------------------------------------
# 30E/360 Eurobond  (ISDA 2006 Section 4.16(g))
# ---------------------------------------------------------------------------


def thirty_e_360(d1: datetime.date, d2: datetime.date) -> float:
    """Return the 30E/360 Eurobond year fraction.

    Adjustment rules:

    * If D1 == 31, set D1 = 30.
    * If D2 == 31, set D2 = 30.

    No end-of-February adjustment is applied -- that is the defining
    difference from the 30/360 US convention.

    Year fraction = ((Y2 - Y1)*360 + (M2 - M1)*30 + (D2_adj - D1_adj)) / 360

    Parameters
    ----------
    d1:
        Start date (inclusive).
    d2:
        End date (exclusive).

    Raises
    ------
    ValueError
        If d2 < d1.
    """
    _validate(d1, d2)

    y1, m1, dd1 = d1.year, d1.month, d1.day
    y2, m2, dd2 = d2.year, d2.month, d2.day

    if dd1 == 31:
        dd1 = 30
    if dd2 == 31:
        dd2 = 30

    numerator = (y2 - y1) * 360 + (m2 - m1) * 30 + (dd2 - dd1)
    return numerator / 360.0
