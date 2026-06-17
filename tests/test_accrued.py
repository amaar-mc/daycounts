"""Tests for the accrued_interest helper."""

from __future__ import annotations

import datetime

import pytest

from daycounts import Convention, accrued_interest, year_fraction


def d(year: int, month: int, day: int) -> datetime.date:
    return datetime.date(year, month, day)


class TestAccruedInterest:
    def test_basic_actual_360(self) -> None:
        # face=1_000_000, rate=5%, d1=2024-01-01, d2=2024-07-01
        # days = Jan31+Feb29+Mar31+Apr30+May31+Jun30 = 182
        # accrued = 1_000_000 * 0.05 * (182/360) = 25_277.777...
        result = accrued_interest(1_000_000.0, 0.05, d(2024, 1, 1), d(2024, 7, 1), "actual/360")
        assert result == pytest.approx(1_000_000 * 0.05 * (182 / 360.0))

    def test_zero_rate(self) -> None:
        result = accrued_interest(1_000_000.0, 0.0, d(2024, 1, 1), d(2024, 7, 1), "actual/360")
        assert result == pytest.approx(0.0)

    def test_zero_face(self) -> None:
        result = accrued_interest(0.0, 0.05, d(2024, 1, 1), d(2024, 7, 1), "actual/365f")
        assert result == pytest.approx(0.0)

    def test_equals_face_times_rate_times_yf(self) -> None:
        # accrued_interest must equal face * rate * year_fraction(...)
        face = 500_000.0
        rate = 0.06
        d1 = d(2023, 11, 1)
        d2 = d(2024, 5, 1)
        for conv in Convention:
            expected = face * rate * year_fraction(d1, d2, conv)
            result = accrued_interest(face, rate, d1, d2, conv)
            assert result == pytest.approx(expected), f"conv={conv}"

    def test_unknown_convention_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown convention"):
            accrued_interest(1_000_000.0, 0.05, d(2024, 1, 1), d(2024, 7, 1), "bad/basis")

    def test_d2_before_d1_raises(self) -> None:
        with pytest.raises(ValueError, match="d2"):
            accrued_interest(1_000_000.0, 0.05, d(2024, 7, 1), d(2024, 1, 1), "actual/360")
