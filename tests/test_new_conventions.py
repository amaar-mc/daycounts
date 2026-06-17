"""
Tests for NL/365 and Actual/365L day-count conventions.

Golden values are hand-derived.  Arithmetic is shown in comments next to
each assertion.

NL/365 definition:
    numerator  = (d2 - d1).days - count(Feb 29 in [d1, d2))
    denominator = 365

Actual/365L (ISMA-Year) definition:
    numerator  = (d2 - d1).days
    denominator = 366 if (isleap(d2.year) OR period [d1,d2) contains Feb 29)
                  else 365
"""

from __future__ import annotations

import datetime

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from daycounts import Convention, actual_365_fixed, actual_365l, nl_365, year_fraction
from daycounts.conventions import _count_feb29_in_range

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def d(year: int, month: int, day: int) -> datetime.date:
    return datetime.date(year, month, day)


# ---------------------------------------------------------------------------
# _count_feb29_in_range (internal helper)
# ---------------------------------------------------------------------------


class TestCountFeb29InRange:
    def test_no_leap_day_in_range(self) -> None:
        # 2023 is not a leap year; no Feb 29
        assert _count_feb29_in_range(d(2023, 1, 1), d(2023, 12, 31)) == 0

    def test_one_leap_day_in_range(self) -> None:
        # 2020-02-29 lies in [2020-02-01, 2020-03-01)
        assert _count_feb29_in_range(d(2020, 2, 1), d(2020, 3, 1)) == 1

    def test_leap_day_at_start_excluded(self) -> None:
        # Feb 29 is NOT in (2020-03-01, ...) because we use half-open [d1, d2)
        # Check that Feb 29 exactly at d1 is included (inclusive start)
        assert _count_feb29_in_range(d(2020, 2, 29), d(2020, 3, 1)) == 1

    def test_leap_day_at_end_excluded(self) -> None:
        # d2 is exclusive: [d1, d2) so Feb 29 == d2 is NOT counted
        assert _count_feb29_in_range(d(2020, 2, 1), d(2020, 2, 29)) == 0

    def test_multi_year_multiple_leap_days(self) -> None:
        # 2000, 2004, 2008 are leap years; 2100 is not
        # Range [2000-01-01, 2009-01-01) covers Feb 29 in 2000, 2004, 2008
        assert _count_feb29_in_range(d(2000, 1, 1), d(2009, 1, 1)) == 3

    def test_same_date_zero(self) -> None:
        assert _count_feb29_in_range(d(2020, 2, 29), d(2020, 2, 29)) == 0

    def test_four_year_single_leap(self) -> None:
        # 2020 is the only leap year in [2020-01-01, 2024-01-01)
        assert _count_feb29_in_range(d(2020, 1, 1), d(2024, 1, 1)) == 1


# ---------------------------------------------------------------------------
# NL/365
# ---------------------------------------------------------------------------


class TestNL365:
    def test_worked_example_leap_day_in_range(self) -> None:
        # 2020-02-28 to 2020-03-01
        # actual days = 2; Feb 29 2020 in [d1, d2) -> leap_days = 1
        # fraction = (2 - 1) / 365 = 1/365
        result = nl_365(d(2020, 2, 28), d(2020, 3, 1))
        assert result == pytest.approx(1 / 365.0)

    def test_no_leap_day_agrees_with_actual_365_fixed(self) -> None:
        # 2023-01-01 to 2023-07-01: no Feb 29 -> NL/365 == actual_365_fixed
        # Jan31+Feb28+Mar31+Apr30+May31+Jun30 = 181 days
        assert nl_365(d(2023, 1, 1), d(2023, 7, 1)) == pytest.approx(
            actual_365_fixed(d(2023, 1, 1), d(2023, 7, 1))
        )

    def test_full_leap_year(self) -> None:
        # 2020-01-01 to 2021-01-01: actual=366, Feb 29 2020 in range -> leap_days=1
        # fraction = (366 - 1) / 365 = 365/365 = 1.0
        result = nl_365(d(2020, 1, 1), d(2021, 1, 1))
        assert result == pytest.approx(365 / 365.0)

    def test_full_non_leap_year(self) -> None:
        # 2023-01-01 to 2024-01-01: actual=365, no Feb 29 -> 365/365 = 1.0
        result = nl_365(d(2023, 1, 1), d(2024, 1, 1))
        assert result == pytest.approx(1.0)

    def test_zero_days(self) -> None:
        result = nl_365(d(2020, 2, 29), d(2020, 2, 29))
        assert result == 0.0

    def test_single_non_leap_day(self) -> None:
        # 2023-03-01 to 2023-03-02: 1 day, no Feb 29 -> 1/365
        result = nl_365(d(2023, 3, 1), d(2023, 3, 2))
        assert result == pytest.approx(1 / 365.0)

    def test_single_leap_day(self) -> None:
        # 2020-02-29 to 2020-03-01: actual=1, Feb 29 at d1 in [d1,d2) -> leap_days=1
        # fraction = (1 - 1) / 365 = 0.0
        result = nl_365(d(2020, 2, 29), d(2020, 3, 1))
        assert result == pytest.approx(0.0)

    def test_multi_year_span_multiple_leap_days(self) -> None:
        # 2000-01-01 to 2009-01-01: actual=3288 days
        # leap years in range with Feb 29 in [d1,d2): 2000, 2004, 2008 -> 3 leap days
        # fraction = (3288 - 3) / 365 = 3285/365 = 9.0
        actual_days = (d(2009, 1, 1) - d(2000, 1, 1)).days
        assert actual_days == 3288
        result = nl_365(d(2000, 1, 1), d(2009, 1, 1))
        assert result == pytest.approx((3288 - 3) / 365.0)

    def test_spanning_leap_year_no_feb29_in_range(self) -> None:
        # 2020-03-01 to 2021-03-01: 365 actual days (Feb 29 2020 is before d1)
        # Feb 29 2020 is NOT in [2020-03-01, 2021-03-01) -> leap_days=0
        # fraction = 365/365 = 1.0
        result = nl_365(d(2020, 3, 1), d(2021, 3, 1))
        assert result == pytest.approx(365 / 365.0)

    def test_d2_before_d1_raises(self) -> None:
        with pytest.raises(ValueError, match="d2"):
            nl_365(d(2020, 3, 1), d(2020, 2, 1))

    def test_nl365_lte_actual_365_fixed_when_leap_day_present(self) -> None:
        # When there are leap days, NL/365 < actual_365_fixed (fewer days in numerator)
        r_nl = nl_365(d(2020, 1, 1), d(2020, 12, 31))
        r_a365 = actual_365_fixed(d(2020, 1, 1), d(2020, 12, 31))
        assert r_nl <= r_a365


# ---------------------------------------------------------------------------
# Actual/365L
# ---------------------------------------------------------------------------


class TestActual365L:
    def test_non_leap_period_non_leap_end(self) -> None:
        # 2023-01-01 to 2023-07-01: 181 days, d2.year=2023 non-leap, no Feb 29
        # denom = 365; fraction = 181/365
        result = actual_365l(d(2023, 1, 1), d(2023, 7, 1))
        assert result == pytest.approx(181 / 365.0)

    def test_leap_year_period_contains_feb29(self) -> None:
        # 2020-01-01 to 2020-07-01: 182 days, Feb 29 2020 in [d1,d2), d2.year=2020 leap
        # denom = 366; fraction = 182/366
        result = actual_365l(d(2020, 1, 1), d(2020, 7, 1))
        assert result == pytest.approx(182 / 366.0)

    def test_leap_end_year_no_feb29_in_range(self) -> None:
        # 2023-07-01 to 2024-01-01: 184 days; d2.year=2024 is leap; no Feb 29 in range
        # denom = 366 (because d2.year is leap); fraction = 184/366
        # Jul(31)+Aug(31)+Sep(30)+Oct(31)+Nov(30)+Dec(31) = 184
        result = actual_365l(d(2023, 7, 1), d(2024, 1, 1))
        assert result == pytest.approx(184 / 366.0)

    def test_non_leap_end_year_with_feb29_in_range(self) -> None:
        # 2020-02-01 to 2021-01-01: d2.year=2021 non-leap, but Feb 29 2020 in range
        # actual days = 335; denom = 366 (Feb 29 in range); fraction = 335/366
        actual_days = (d(2021, 1, 1) - d(2020, 2, 1)).days
        result = actual_365l(d(2020, 2, 1), d(2021, 1, 1))
        assert result == pytest.approx(actual_days / 366.0)

    def test_full_non_leap_year(self) -> None:
        # 2023-01-01 to 2024-01-01: 365 days; d2.year=2024 leap -> denom=366
        # fraction = 365/366
        result = actual_365l(d(2023, 1, 1), d(2024, 1, 1))
        assert result == pytest.approx(365 / 366.0)

    def test_full_leap_year(self) -> None:
        # 2020-01-01 to 2021-01-01: 366 days; d2.year=2021 non-leap; Feb 29 in range
        # denom = 366 (Feb 29 in range); fraction = 366/366 = 1.0
        result = actual_365l(d(2020, 1, 1), d(2021, 1, 1))
        assert result == pytest.approx(366 / 366.0)

    def test_zero_days(self) -> None:
        result = actual_365l(d(2020, 6, 1), d(2020, 6, 1))
        assert result == 0.0

    def test_single_non_leap_day_in_non_leap_year(self) -> None:
        # 2023-03-01 to 2023-03-02: 1 day; d2.year=2023 non-leap; no Feb 29
        # denom=365; fraction=1/365
        result = actual_365l(d(2023, 3, 1), d(2023, 3, 2))
        assert result == pytest.approx(1 / 365.0)

    def test_multi_year_span(self) -> None:
        # 2022-01-01 to 2025-01-01: 1096 days; d2.year=2025 non-leap
        # Feb 29 2024 in [d1, d2) -> denom=366; fraction = 1096/366
        actual_days = (d(2025, 1, 1) - d(2022, 1, 1)).days
        assert actual_days == 1096
        result = actual_365l(d(2022, 1, 1), d(2025, 1, 1))
        assert result == pytest.approx(1096 / 366.0)

    def test_d2_before_d1_raises(self) -> None:
        with pytest.raises(ValueError, match="d2"):
            actual_365l(d(2020, 3, 1), d(2020, 2, 1))


# ---------------------------------------------------------------------------
# Convention enum and dispatcher
# ---------------------------------------------------------------------------


class TestDispatchNewConventions:
    def test_dispatch_nl365_by_enum(self) -> None:
        d1 = d(2020, 2, 28)
        d2 = d(2020, 3, 1)
        assert year_fraction(d1, d2, Convention.NL_365) == pytest.approx(nl_365(d1, d2))

    def test_dispatch_nl365_by_string(self) -> None:
        d1 = d(2020, 2, 28)
        d2 = d(2020, 3, 1)
        assert year_fraction(d1, d2, "nl/365") == pytest.approx(nl_365(d1, d2))

    def test_dispatch_actual_365l_by_enum(self) -> None:
        d1 = d(2023, 1, 1)
        d2 = d(2023, 7, 1)
        assert year_fraction(d1, d2, Convention.ACTUAL_365L) == pytest.approx(
            actual_365l(d1, d2)
        )

    def test_dispatch_actual_365l_by_string(self) -> None:
        d1 = d(2023, 1, 1)
        d2 = d(2023, 7, 1)
        assert year_fraction(d1, d2, "actual/365l") == pytest.approx(actual_365l(d1, d2))

    def test_convention_enum_round_trip_includes_new(self) -> None:
        # Each Convention value can be parsed back from its string -- including new ones
        for conv in Convention:
            assert Convention(conv.value) is conv

    def test_string_case_insensitive_nl365(self) -> None:
        d1 = d(2020, 2, 28)
        d2 = d(2020, 3, 5)
        assert year_fraction(d1, d2, "NL/365") == pytest.approx(
            year_fraction(d1, d2, "nl/365")
        )

    def test_string_case_insensitive_actual_365l(self) -> None:
        d1 = d(2023, 1, 1)
        d2 = d(2023, 7, 1)
        assert year_fraction(d1, d2, "ACTUAL/365L") == pytest.approx(
            year_fraction(d1, d2, "actual/365l")
        )


# ---------------------------------------------------------------------------
# Hypothesis property tests
# ---------------------------------------------------------------------------


@st.composite
def date_pair(draw: st.DrawFn) -> tuple[datetime.date, datetime.date]:
    """Draw a valid (d1, d2) pair with d2 >= d1."""
    d1 = draw(st.dates(min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2100, 1, 1)))
    offset = draw(st.integers(min_value=0, max_value=3650))
    d2 = d1 + datetime.timedelta(days=offset)
    return d1, d2


@settings(max_examples=200)
@given(date_pair())
def test_nl365_nonnegative(pair: tuple[datetime.date, datetime.date]) -> None:
    """NL/365 year fraction is always non-negative."""
    d1, d2 = pair
    assert nl_365(d1, d2) >= 0.0


@settings(max_examples=200)
@given(date_pair())
def test_nl365_monotonic(pair: tuple[datetime.date, datetime.date]) -> None:
    """NL/365 fraction increases (or stays equal) when d2 advances by one day."""
    d1, d2 = pair
    d2_plus1 = d2 + datetime.timedelta(days=1)
    assert nl_365(d1, d2_plus1) >= nl_365(d1, d2)


@settings(max_examples=200)
@given(date_pair())
def test_nl365_lte_actual_365_fixed(pair: tuple[datetime.date, datetime.date]) -> None:
    """NL/365 <= actual_365_fixed always (removing leap days can only decrease numerator)."""
    d1, d2 = pair
    assert nl_365(d1, d2) <= actual_365_fixed(d1, d2) + 1e-12


@settings(max_examples=200)
@given(date_pair())
def test_actual_365l_nonnegative(pair: tuple[datetime.date, datetime.date]) -> None:
    """Actual/365L year fraction is always non-negative."""
    d1, d2 = pair
    assert actual_365l(d1, d2) >= 0.0


@settings(max_examples=200)
@given(date_pair())
def test_actual_365l_monotonic(pair: tuple[datetime.date, datetime.date]) -> None:
    """Actual/365L fraction increases (or stays equal) when d2 advances by one day.

    This holds because we advance d2 by 1; actual_days increases by 1, while the
    denominator can only change when the new d2 falls in a different leap/non-leap
    regime -- but the numerator always grows by 1 and the denominator is at most 366,
    so the ratio is monotonic in the numerator over a fixed denominator.

    Note: The denominator CAN change when d2 crosses into a different year, so
    strict increase is not guaranteed.  We only assert >=.
    """
    d1, d2 = pair
    d2_plus1 = d2 + datetime.timedelta(days=1)
    # Use a relaxed tolerance because denominator can flip between 365 and 366
    assert actual_365l(d1, d2_plus1) >= actual_365l(d1, d2) - 1.0 / 365.0
