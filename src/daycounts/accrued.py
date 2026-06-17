"""
Accrued interest helper.

Computes the accrued interest on a fixed-rate instrument over a period
using any supported day-count convention.
"""

from __future__ import annotations

import datetime

from daycounts.dispatcher import Convention, year_fraction


def accrued_interest(
    face: float,
    rate: float,
    d1: datetime.date,
    d2: datetime.date,
    convention: Convention | str,
) -> float:
    """Return the accrued interest on a fixed-rate instrument.

    Accrued interest = face * rate * year_fraction(d1, d2, convention)

    Parameters
    ----------
    face:
        Notional (face value) of the instrument.
    rate:
        Annual coupon rate as a decimal (e.g. 0.05 for 5%).
    d1:
        Accrual start date (inclusive).
    d2:
        Accrual end date (exclusive).
    convention:
        Day-count convention -- a Convention member or its string value.

    Returns
    -------
    float
        Accrued interest in the same units as ``face``.

    Raises
    ------
    ValueError
        If d2 < d1, or if ``convention`` is not recognized.

    Examples
    --------
    >>> import datetime
    >>> accrued_interest(
    ...     1_000_000, 0.05,
    ...     datetime.date(2024, 1, 1), datetime.date(2024, 7, 1),
    ...     'actual/360',
    ... )
    25277.777777777777
    """
    yf = year_fraction(d1, d2, convention)
    return face * rate * yf
