"""
Financial day-count convention implementations.

Each function accepts two datetime.date objects d1 (start, inclusive) and
d2 (end, exclusive) and returns a float year fraction according to the
convention defined in ISDA 2006 Definitions, Section 4.16.

References
----------
ISDA 2006 Definitions, Section 4.16 (Day Count Fractions).
ISMA Rule Book (2001) for Actual/365L (ISMA-Year).
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


# ---------------------------------------------------------------------------
# Helpers for leap-day counting
# ---------------------------------------------------------------------------


def _count_feb29_in_range(d1: datetime.date, d2: datetime.date) -> int:
    """Return the count of February 29 occurrences in the half-open interval [d1, d2).

    Only dates where calendar.isleap(year) and year has a Feb 29 that lies
    within [d1, d2) are counted.  Handles multi-year ranges correctly.

    Parameters
    ----------
    d1:
        Interval start (inclusive).
    d2:
        Interval end (exclusive).
    """
    count = 0
    for year in range(d1.year, d2.year + 1):
        if not calendar.isleap(year):
            continue
        feb29 = datetime.date(year, 2, 29)
        if d1 <= feb29 < d2:
            count += 1
    return count


# ---------------------------------------------------------------------------
# NL/365 (Actual/365 No-Leap)
# ---------------------------------------------------------------------------


def nl_365(d1: datetime.date, d2: datetime.date) -> float:
    """Return the NL/365 (Actual/365 No-Leap) year fraction.

    Also known as Actual/365 No-Leap.

    Numerator = actual days between d1 and d2 minus the number of February 29
    occurrences in the half-open interval [d1, d2).
    Denominator = 365.

    Year fraction = (actual_days - leap_days) / 365

    Worked example:
        d1 = 2020-02-28, d2 = 2020-03-01
        actual days = 2; Feb 29 2020 lies in [d1, d2) -> leap_days = 1
        year fraction = (2 - 1) / 365 = 1/365

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
    For periods that contain no Feb 29, NL/365 agrees with Actual/365 Fixed.
    NL/365 is used in some UK gilt and money-market contexts where leap-day
    inflation is undesirable.
    """
    _validate(d1, d2)
    actual_days = (d2 - d1).days
    leap_days = _count_feb29_in_range(d1, d2)
    return (actual_days - leap_days) / 365.0


# ---------------------------------------------------------------------------
# Actual/365L (Actual/365 Leap-year, ISMA-Year)
# ---------------------------------------------------------------------------


def actual_365l(d1: datetime.date, d2: datetime.date) -> float:
    """Return the Actual/365L (Actual/365 Leap-year, ISMA-Year) year fraction.

    Also known as ISMA-Year.

    Numerator = actual days between d1 and d2.
    Denominator = 366 if either:
        (a) the period [d1, d2) contains a February 29, or
        (b) d2's year is a leap year;
    otherwise 365.

    Precisely: denom = 366 if (calendar.isleap(d2.year) or
    _count_feb29_in_range(d1, d2) > 0) else 365.

    Year fraction = actual_days / denom

    Worked examples:
        Non-leap: d1 = 2023-01-01, d2 = 2023-07-01 (181 days, non-leap end)
            -> denom = 365, fraction = 181/365
        Leap-containing: d1 = 2020-01-01, d2 = 2020-07-01 (182 days, leap year
            2020 contains Feb 29)
            -> denom = 366, fraction = 182/366
        Leap end-year: d1 = 2023-07-01, d2 = 2024-01-01 (184 days, d2 in leap
            year 2024)
            -> denom = 366, fraction = 184/366

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
    Rule per ISMA Rule Book (2001) and widespread market practice: use 366
    whenever Feb 29 falls in the coupon period or the coupon period ends in a
    leap year; otherwise use 365.  This ensures the denominator reflects the
    actual length of the year containing the accrual end.

    Reference: ISMA (International Securities Market Association) Rule Book,
    Appendix A (2001); also documented in OpenGamma Strata as
    DayCounts.ACT_365L.
    """
    _validate(d1, d2)
    actual_days = (d2 - d1).days
    contains_feb29 = _count_feb29_in_range(d1, d2) > 0
    denom = 366 if (calendar.isleap(d2.year) or contains_feb29) else 365
    return actual_days / denom
