"""
Tests for individual day-count convention functions.

Golden values are hand-derived from ISDA 2006 Definitions, Section 4.16,
and cross-checked against QuantLib reference examples.  The arithmetic is
shown in comments next to each assertion.
"""

from __future__ import annotations

import datetime

import pytest

from daycounts import (
    Convention,
    actual_360,
    actual_365_fixed,
    actual_actual_isda,
    thirty_360_us,
    thirty_e_360,
    year_fraction,
)

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def d(year: int, month: int, day: int) -> datetime.date:
    return datetime.date(year, month, day)


# ---------------------------------------------------------------------------
# Actual/360
# ---------------------------------------------------------------------------


class TestActual360:
    def test_one_year_non_leap(self) -> None:
        # 2023-01-01 to 2024-01-01: 365 days
        # year fraction = 365 / 360 = 1.01388...
        result = actual_360(d(2023, 1, 1), d(2024, 1, 1))
        assert result == pytest.approx(365 / 360.0)

    def test_one_year_leap(self) -> None:
        # 2024-01-01 to 2025-01-01: 366 days (2024 is leap)
        # year fraction = 366 / 360 = 1.01666...
        result = actual_360(d(2024, 1, 1), d(2025, 1, 1))
        assert result == pytest.approx(366 / 360.0)

    def test_n_day_span(self) -> None:
        # 90-day quarter: 90 / 360 = 0.25
        result = actual_360(d(2024, 1, 1), d(2024, 4, 1))
        assert result == pytest.approx(91 / 360.0)  # Jan(31)+Feb(29)+Mar(31)=91

    def test_zero_days(self) -> None:
        result = actual_360(d(2024, 6, 1), d(2024, 6, 1))
        assert result == 0.0

    def test_d2_before_d1_raises(self) -> None:
        with pytest.raises(ValueError, match="d2"):
            actual_360(d(2024, 6, 2), d(2024, 6, 1))

    def test_single_day(self) -> None:
        # 1 day: 1 / 360
        result = actual_360(d(2024, 3, 1), d(2024, 3, 2))
        assert result == pytest.approx(1 / 360.0)


# ---------------------------------------------------------------------------
# Actual/365 Fixed
# ---------------------------------------------------------------------------


class TestActual365Fixed:
    def test_one_year_non_leap(self) -> None:
        # 2023-01-01 to 2024-01-01: 365 days
        # year fraction = 365 / 365 = 1.0
        result = actual_365_fixed(d(2023, 1, 1), d(2024, 1, 1))
        assert result == pytest.approx(1.0)

    def test_one_year_leap(self) -> None:
        # 2024-01-01 to 2025-01-01: 366 days
        # year fraction = 366 / 365 = 1.00273...
        result = actual_365_fixed(d(2024, 1, 1), d(2025, 1, 1))
        assert result == pytest.approx(366 / 365.0)

    def test_half_year(self) -> None:
        # 2024-01-01 to 2024-07-01: 182 days (Jan31+Feb29+Mar31+Apr30+May31+Jun30)
        result = actual_365_fixed(d(2024, 1, 1), d(2024, 7, 1))
        # 31+29+31+30+31+30 = 182
        assert result == pytest.approx(182 / 365.0)

    def test_d2_before_d1_raises(self) -> None:
        with pytest.raises(ValueError, match="d2"):
            actual_365_fixed(d(2024, 6, 2), d(2024, 6, 1))


# ---------------------------------------------------------------------------
# Actual/Actual ISDA
# ---------------------------------------------------------------------------


class TestActualActualISDA:
    def test_within_non_leap_year(self) -> None:
        # 2023-01-01 to 2023-07-01: 181 days, all in non-leap 2023
        # year fraction = 181 / 365 = 0.49589...
        # Jan31+Feb28+Mar31+Apr30+May31+Jun30 = 181
        result = actual_actual_isda(d(2023, 1, 1), d(2023, 7, 1))
        assert result == pytest.approx(181 / 365.0)

    def test_within_leap_year(self) -> None:
        # 2024-01-01 to 2024-07-01: 182 days, all in leap 2024
        # year fraction = 182 / 366 = 0.49726...
        # Jan31+Feb29+Mar31+Apr30+May31+Jun30 = 182
        result = actual_actual_isda(d(2024, 1, 1), d(2024, 7, 1))
        assert result == pytest.approx(182 / 366.0)

    def test_crossing_year_boundary_non_to_non_leap(self) -> None:
        # 2022-07-01 to 2023-07-01 (spanning both non-leap years)
        # In 2022: 2022-07-01 to 2023-01-01 = 184 days / 365
        # In 2023: 2023-01-01 to 2023-07-01 = 181 days / 365
        # Total = (184 + 181) / 365 = 365 / 365 = 1.0
        result = actual_actual_isda(d(2022, 7, 1), d(2023, 7, 1))
        # 2022 days: Jul(31)+Aug(31)+Sep(30)+Oct(31)+Nov(30)+Dec(31) = 184
        # 2023 days: Jan(31)+Feb(28)+Mar(31)+Apr(30)+May(31)+Jun(30) = 181
        assert result == pytest.approx(184 / 365.0 + 181 / 365.0)

    def test_crossing_leap_year_boundary(self) -> None:
        # ISDA 2006 example: 2003-11-01 to 2004-05-01
        # In 2003 (non-leap): 2003-11-01 to 2004-01-01 = 61 days / 365
        # In 2004 (leap):     2004-01-01 to 2004-05-01 = 121 days / 366
        # Nov(30)+Dec(31) = 61 in 2003
        # Jan(31)+Feb(29)+Mar(31)+Apr(30) = 121 in 2004
        result = actual_actual_isda(d(2003, 11, 1), d(2004, 5, 1))
        expected = 61 / 365.0 + 121 / 366.0
        assert result == pytest.approx(expected)

    def test_exact_one_year_non_leap(self) -> None:
        # 2023-01-01 to 2024-01-01 entirely in non-leap 2023 = 365/365 = 1.0
        result = actual_actual_isda(d(2023, 1, 1), d(2024, 1, 1))
        assert result == pytest.approx(1.0)

    def test_exact_one_year_leap(self) -> None:
        # 2024-01-01 to 2025-01-01: 366 days in leap 2024 = 366/366 = 1.0
        result = actual_actual_isda(d(2024, 1, 1), d(2025, 1, 1))
        assert result == pytest.approx(1.0)

    def test_multi_year_span(self) -> None:
        # 2022-01-01 to 2025-01-01: three full years (2022, 2023 non-leap; 2024 leap)
        # 365/365 + 365/365 + 366/366 = 3.0
        result = actual_actual_isda(d(2022, 1, 1), d(2025, 1, 1))
        assert result == pytest.approx(3.0)

    def test_zero_days(self) -> None:
        result = actual_actual_isda(d(2024, 6, 1), d(2024, 6, 1))
        assert result == 0.0

    def test_d2_before_d1_raises(self) -> None:
        with pytest.raises(ValueError, match="d2"):
            actual_actual_isda(d(2024, 6, 2), d(2024, 6, 1))


# ---------------------------------------------------------------------------
# 30/360 US Bond Basis
# ---------------------------------------------------------------------------


class TestThirty360US:
    def test_basic_quarter(self) -> None:
        # 2024-01-01 to 2024-04-01: no adjustments needed
        # (0*360 + 3*30 + 0) / 360 = 90/360 = 0.25
        result = thirty_360_us(d(2024, 1, 1), d(2024, 4, 1))
        assert result == pytest.approx(90 / 360.0)

    def test_d1_on_31st(self) -> None:
        # D1=31 -> adjusted to 30
        # 2024-01-31 to 2024-04-30
        # After: D1=30, D2=30 (D2 is 30, not 31, so no step-3 change)
        # (0*360 + 3*30 + (30-30)) / 360 = 90/360 = 0.25
        result = thirty_360_us(d(2024, 1, 31), d(2024, 4, 30))
        assert result == pytest.approx(90 / 360.0)

    def test_d2_on_31st_when_d1_on_30th(self) -> None:
        # D1=30 (after adjustment), D2=31 -> D2 adjusted to 30
        # 2024-01-30 to 2024-04-31 -> but April has 30 days
        # Use: 2024-01-30 to 2024-03-31
        # D1=30, D2=31, D1 in {30,31} so D2->30
        # (0*360 + 2*30 + (30-30)) / 360 = 60/360 = 0.1666...
        result = thirty_360_us(d(2024, 1, 30), d(2024, 3, 31))
        # D1=30 (already), D2=31, D1 in {30,31} -> D2=30
        # (0*360 + 2*30 + (30-30)) / 360 = 60/360
        assert result == pytest.approx(60 / 360.0)

    def test_d1_31_d2_31(self) -> None:
        # 2024-01-31 to 2024-03-31: D1=31->30, D2=31 and D1 in {30,31}->D2=30
        # (0*360 + 2*30 + (30-30)) / 360 = 60/360 = 0.1666...
        result = thirty_360_us(d(2024, 1, 31), d(2024, 3, 31))
        assert result == pytest.approx(60 / 360.0)

    def test_d1_feb_end_d2_feb_end(self) -> None:
        # 2024-02-29 (leap Feb end) to 2025-02-28 (non-leap Feb end)
        # Step 1: both last-Feb -> D2=30; Step 2: D1 last-Feb -> D1=30
        # (1*360 + 0*30 + (30-30)) / 360 = 360/360 = 1.0
        result = thirty_360_us(d(2024, 2, 29), d(2025, 2, 28))
        assert result == pytest.approx(360 / 360.0)

    def test_d1_feb28_non_leap_d2_not_feb_end(self) -> None:
        # 2023-02-28 is the last day of February in a non-leap year
        # d2 = 2023-05-31 (not end of Feb)
        # Step 1 not triggered (d2 not end of Feb)
        # Step 2: D1 is last-Feb -> D1=30
        # D2=31, D1=30 in {30,31} -> D2=30 (step 3)
        # (0*360 + 3*30 + (30-30)) / 360 = 90/360 = 0.25
        result = thirty_360_us(d(2023, 2, 28), d(2023, 5, 31))
        assert result == pytest.approx(90 / 360.0)

    def test_d1_feb29_leap_only_d1_is_feb_end(self) -> None:
        # 2024-02-29 (last Feb in leap) to 2024-05-29
        # Step 1: D2 is 2024-05-29, not end of Feb -> skip
        # Step 2: D1 is last-Feb -> D1=30
        # D2=29, not 31, no step-3
        # D1=30 already, no step-4
        # (0*360 + 3*30 + (29-30)) / 360 = (90-1)/360 = 89/360
        result = thirty_360_us(d(2024, 2, 29), d(2024, 5, 29))
        assert result == pytest.approx(89 / 360.0)

    def test_one_year(self) -> None:
        # 2024-01-01 to 2025-01-01: exactly 1 year
        # (1*360 + 0*30 + 0) / 360 = 1.0
        result = thirty_360_us(d(2024, 1, 1), d(2025, 1, 1))
        assert result == pytest.approx(1.0)

    def test_d2_before_d1_raises(self) -> None:
        with pytest.raises(ValueError, match="d2"):
            thirty_360_us(d(2024, 6, 2), d(2024, 6, 1))


# ---------------------------------------------------------------------------
# 30E/360 Eurobond
# ---------------------------------------------------------------------------


class TestThirtyE360:
    def test_basic_quarter(self) -> None:
        # 2024-01-01 to 2024-04-01: no adjustment
        # (0*360 + 3*30 + 0) / 360 = 0.25
        result = thirty_e_360(d(2024, 1, 1), d(2024, 4, 1))
        assert result == pytest.approx(90 / 360.0)

    def test_d1_on_31st(self) -> None:
        # D1=31->30; D2=30 (no change)
        # 2024-01-31 to 2024-04-30: (0*360+3*30+(30-30))/360 = 90/360
        result = thirty_e_360(d(2024, 1, 31), d(2024, 4, 30))
        assert result == pytest.approx(90 / 360.0)

    def test_d2_on_31st(self) -> None:
        # D1=1, D2=31->30
        # 2024-01-01 to 2024-03-31: (0*360+2*30+(30-1))/360 = (60+29)/360 = 89/360
        result = thirty_e_360(d(2024, 1, 1), d(2024, 3, 31))
        assert result == pytest.approx(89 / 360.0)

    def test_no_feb_adjustment(self) -> None:
        # 30E/360 has NO end-of-February special rule
        # 2024-02-29 to 2025-02-28
        # D1=29 (not 31, no adjustment), D2=28 (not 31, no adjustment)
        # (1*360 + 0*30 + (28-29)) / 360 = (360-1)/360 = 359/360
        result = thirty_e_360(d(2024, 2, 29), d(2025, 2, 28))
        assert result == pytest.approx(359 / 360.0)

    def test_one_year(self) -> None:
        # 2024-01-01 to 2025-01-01 = 1.0
        result = thirty_e_360(d(2024, 1, 1), d(2025, 1, 1))
        assert result == pytest.approx(1.0)

    def test_d2_before_d1_raises(self) -> None:
        with pytest.raises(ValueError, match="d2"):
            thirty_e_360(d(2024, 6, 2), d(2024, 6, 1))


# ---------------------------------------------------------------------------
# year_fraction dispatcher
# ---------------------------------------------------------------------------


class TestYearFraction:
    def test_dispatch_by_enum(self) -> None:
        d1 = d(2023, 1, 1)
        d2 = d(2024, 1, 1)
        assert year_fraction(d1, d2, Convention.ACTUAL_360) == pytest.approx(
            actual_360(d1, d2)
        )

    def test_dispatch_by_string(self) -> None:
        d1 = d(2024, 1, 1)
        d2 = d(2025, 1, 1)
        assert year_fraction(d1, d2, "actual/360") == pytest.approx(actual_360(d1, d2))

    def test_dispatch_actual_365_fixed(self) -> None:
        d1 = d(2023, 1, 1)
        d2 = d(2024, 1, 1)
        assert year_fraction(d1, d2, Convention.ACTUAL_365_FIXED) == pytest.approx(
            actual_365_fixed(d1, d2)
        )

    def test_dispatch_actual_actual_isda(self) -> None:
        d1 = d(2003, 11, 1)
        d2 = d(2004, 5, 1)
        assert year_fraction(d1, d2, Convention.ACTUAL_ACTUAL_ISDA) == pytest.approx(
            actual_actual_isda(d1, d2)
        )

    def test_dispatch_thirty_360_us(self) -> None:
        d1 = d(2024, 1, 1)
        d2 = d(2024, 4, 1)
        assert year_fraction(d1, d2, Convention.THIRTY_360_US) == pytest.approx(
            thirty_360_us(d1, d2)
        )

    def test_dispatch_thirty_e_360(self) -> None:
        d1 = d(2024, 1, 1)
        d2 = d(2024, 4, 1)
        assert year_fraction(d1, d2, Convention.THIRTY_E_360) == pytest.approx(
            thirty_e_360(d1, d2)
        )

    def test_string_case_insensitive(self) -> None:
        d1 = d(2024, 1, 1)
        d2 = d(2024, 4, 1)
        assert year_fraction(d1, d2, "ACTUAL/360") == pytest.approx(
            year_fraction(d1, d2, "actual/360")
        )

    def test_unknown_convention_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown convention"):
            year_fraction(d(2024, 1, 1), d(2024, 4, 1), "unknown/365")

    def test_convention_enum_round_trip(self) -> None:
        # Each Convention value can be parsed back from its string
        for conv in Convention:
            assert Convention(conv.value) is conv


# ---------------------------------------------------------------------------
# Property-style tests
# ---------------------------------------------------------------------------


class TestProperties:
    def test_actual_360_n_day_span(self) -> None:
        # For any n-day span, actual_360 == n / 360
        for n in (1, 7, 30, 90, 180, 365, 366):
            d1 = datetime.date(2024, 1, 1)
            d2 = d1 + datetime.timedelta(days=n)
            assert actual_360(d1, d2) == pytest.approx(n / 360.0), f"n={n}"

    def test_actual_365_fixed_n_day_span(self) -> None:
        # For any n-day span, actual_365_fixed == n / 365
        for n in (1, 7, 30, 90, 180, 365, 366):
            d1 = datetime.date(2024, 1, 1)
            d2 = d1 + datetime.timedelta(days=n)
            assert actual_365_fixed(d1, d2) == pytest.approx(n / 365.0), f"n={n}"

    def test_year_fraction_matches_direct_function(self) -> None:
        # year_fraction dispatches to the matching direct function
        pairs: list[tuple[Convention, object]] = [
            (Convention.ACTUAL_360, actual_360),
            (Convention.ACTUAL_365_FIXED, actual_365_fixed),
            (Convention.ACTUAL_ACTUAL_ISDA, actual_actual_isda),
            (Convention.THIRTY_360_US, thirty_360_us),
            (Convention.THIRTY_E_360, thirty_e_360),
        ]
        d1 = datetime.date(2024, 3, 15)
        d2 = datetime.date(2024, 9, 15)
        import typing

        for conv, func in pairs:
            direct = typing.cast(
                "typing.Callable[[datetime.date, datetime.date], float]", func
            )(d1, d2)
            assert year_fraction(d1, d2, conv) == pytest.approx(direct), f"conv={conv}"

    def test_additivity_actual_360(self) -> None:
        # year_fraction over [d1, d3] == year_fraction([d1,d2]) + year_fraction([d2,d3])
        d1 = datetime.date(2024, 1, 1)
        d2 = datetime.date(2024, 7, 1)
        d3 = datetime.date(2025, 1, 1)
        assert actual_360(d1, d3) == pytest.approx(
            actual_360(d1, d2) + actual_360(d2, d3)
        )

    def test_additivity_actual_actual_isda(self) -> None:
        d1 = datetime.date(2023, 1, 1)
        d2 = datetime.date(2024, 1, 1)
        d3 = datetime.date(2025, 1, 1)
        assert actual_actual_isda(d1, d3) == pytest.approx(
            actual_actual_isda(d1, d2) + actual_actual_isda(d2, d3)
        )
