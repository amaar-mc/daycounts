"""
Convention enum and year_fraction dispatcher.

The Convention enum defines the canonical names for each supported day-count
convention.  Pass a Convention member (or its string value) to year_fraction
to compute the year fraction under that convention.
"""

from __future__ import annotations

import datetime
import enum

from daycounts.conventions import (
    actual_360,
    actual_365_fixed,
    actual_365l,
    actual_actual_isda,
    nl_365,
    thirty_360_us,
    thirty_e_360,
)


class Convention(str, enum.Enum):
    """Canonical names for supported day-count conventions.

    Members are also valid strings so they can be used as dict keys or
    passed to APIs that expect plain strings.

    Examples
    --------
    >>> Convention.ACTUAL_360
    <Convention.ACTUAL_360: 'actual/360'>
    >>> Convention.ACTUAL_360 == 'actual/360'
    True
    """

    ACTUAL_360 = "actual/360"
    ACTUAL_365_FIXED = "actual/365f"
    ACTUAL_ACTUAL_ISDA = "actual/actual isda"
    THIRTY_360_US = "30/360 us"
    THIRTY_E_360 = "30e/360"
    NL_365 = "nl/365"
    ACTUAL_365L = "actual/365l"


_DISPATCH: dict[Convention, object] = {
    Convention.ACTUAL_360: actual_360,
    Convention.ACTUAL_365_FIXED: actual_365_fixed,
    Convention.ACTUAL_ACTUAL_ISDA: actual_actual_isda,
    Convention.THIRTY_360_US: thirty_360_us,
    Convention.THIRTY_E_360: thirty_e_360,
    Convention.NL_365: nl_365,
    Convention.ACTUAL_365L: actual_365l,
}


def year_fraction(d1: datetime.date, d2: datetime.date, convention: Convention | str) -> float:
    """Return the year fraction between d1 and d2 under the given convention.

    Parameters
    ----------
    d1:
        Start date (inclusive).
    d2:
        End date (exclusive).
    convention:
        A Convention enum member or one of its string values (case-insensitive).
        Supported values:
          - ``'actual/360'``
          - ``'actual/365f'``
          - ``'actual/actual isda'``
          - ``'30/360 us'``
          - ``'30e/360'``
          - ``'nl/365'``
          - ``'actual/365l'``

    Returns
    -------
    float
        Year fraction computed under the selected convention.

    Raises
    ------
    ValueError
        If d2 < d1, or if ``convention`` is not a recognized name.

    Examples
    --------
    >>> import datetime
    >>> year_fraction(datetime.date(2024, 1, 1), datetime.date(2025, 1, 1), 'actual/360')
    1.0166666666666666
    """
    if isinstance(convention, str) and not isinstance(convention, Convention):
        try:
            convention = Convention(convention.lower())
        except ValueError:
            valid = ", ".join(f"'{c.value}'" for c in Convention)
            raise ValueError(
                f"Unknown convention {convention!r}. Valid values: {valid}"
            ) from None

    func = _DISPATCH[convention]
    # mypy: narrow callable
    import typing

    callable_func = typing.cast(
        "typing.Callable[[datetime.date, datetime.date], float]", func
    )
    return callable_func(d1, d2)
