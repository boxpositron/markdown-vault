"""
Tests for date_utils module.

Tests all date formatting functions and offset parsing/application.
"""

from datetime import datetime

import pytest

from markdown_vault.utils.date_utils import (
    apply_offset_daily,
    apply_offset_monthly,
    apply_offset_quarterly,
    apply_offset_weekly,
    apply_offset_yearly,
    format_daily,
    format_monthly,
    format_quarterly,
    format_weekly,
    format_yearly,
    parse_period_offset,
)


class TestFormatting:
    """Test date formatting functions."""

    def test_format_daily(self) -> None:
        """Test daily date formatting."""
        assert format_daily(datetime(2025, 1, 15)) == "2025-01-15"
        assert format_daily(datetime(2025, 12, 31)) == "2025-12-31"
        assert format_daily(datetime(2024, 2, 29)) == "2024-02-29"  # Leap year

    def test_format_weekly(self) -> None:
        """Test weekly date formatting."""
        assert format_weekly(datetime(2025, 1, 1)) == "2025-W01"
        assert format_weekly(datetime(2025, 1, 15)) == "2025-W03"
        # Dec 31, 2025 is Wednesday, which belongs to 2026-W01 in ISO week numbering
        assert format_weekly(datetime(2025, 12, 31)) == "2026-W01"

    def test_format_monthly(self) -> None:
        """Test monthly date formatting."""
        assert format_monthly(datetime(2025, 1, 15)) == "2025-01"
        assert format_monthly(datetime(2025, 12, 1)) == "2025-12"
        assert format_monthly(datetime(2024, 2, 29)) == "2024-02"

    def test_format_quarterly(self) -> None:
        """Test quarterly date formatting."""
        assert format_quarterly(datetime(2025, 1, 15)) == "2025-Q1"
        assert format_quarterly(datetime(2025, 3, 31)) == "2025-Q1"
        assert format_quarterly(datetime(2025, 4, 1)) == "2025-Q2"
        assert format_quarterly(datetime(2025, 7, 1)) == "2025-Q3"
        assert format_quarterly(datetime(2025, 10, 1)) == "2025-Q4"
        assert format_quarterly(datetime(2025, 12, 31)) == "2025-Q4"

    def test_format_yearly(self) -> None:
        """Test yearly date formatting."""
        assert format_yearly(datetime(2025, 1, 1)) == "2025"
        assert format_yearly(datetime(2024, 12, 31)) == "2024"
        assert format_yearly(datetime(2000, 6, 15)) == "2000"


class TestOffsetParsing:
    """Test offset parsing."""

    def test_parse_today(self) -> None:
        """Test parsing 'today' offset."""
        assert parse_period_offset("today") == 0
        assert parse_period_offset("Today") == 0
        assert parse_period_offset("TODAY") == 0

    def test_parse_zero(self) -> None:
        """Test parsing '0' offset."""
        assert parse_period_offset("0") == 0

    def test_parse_positive(self) -> None:
        """Test parsing positive offsets."""
        assert parse_period_offset("+1") == 1
        assert parse_period_offset("+5") == 5
        assert parse_period_offset("+100") == 100
        assert parse_period_offset("1") == 1
        assert parse_period_offset("5") == 5

    def test_parse_negative(self) -> None:
        """Test parsing negative offsets."""
        assert parse_period_offset("-1") == -1
        assert parse_period_offset("-5") == -5
        assert parse_period_offset("-100") == -100

    def test_parse_invalid(self) -> None:
        """Test parsing invalid offsets."""
        with pytest.raises(ValueError, match="Invalid offset format"):
            parse_period_offset("invalid")
        with pytest.raises(ValueError, match="Invalid offset format"):
            parse_period_offset("++1")
        with pytest.raises(ValueError, match="Invalid offset format"):
            parse_period_offset("1.5")


class TestOffsetApplication:
    """Test offset application functions."""

    def test_apply_offset_daily(self) -> None:
        """Test daily offset application."""
        base = datetime(2025, 1, 15)
        assert apply_offset_daily(base, 0) == datetime(2025, 1, 15)
        assert apply_offset_daily(base, 1) == datetime(2025, 1, 16)
        assert apply_offset_daily(base, 7) == datetime(2025, 1, 22)
        assert apply_offset_daily(base, -1) == datetime(2025, 1, 14)
        assert apply_offset_daily(base, -14) == datetime(2025, 1, 1)

    def test_apply_offset_weekly(self) -> None:
        """Test weekly offset application."""
        base = datetime(2025, 1, 15)
        assert apply_offset_weekly(base, 0) == datetime(2025, 1, 15)
        assert apply_offset_weekly(base, 1) == datetime(2025, 1, 22)
        assert apply_offset_weekly(base, -1) == datetime(2025, 1, 8)
        assert apply_offset_weekly(base, 4) == datetime(2025, 2, 12)

    def test_apply_offset_monthly(self) -> None:
        """Test monthly offset application."""
        base = datetime(2025, 1, 15)
        assert apply_offset_monthly(base, 0) == datetime(2025, 1, 15)
        assert apply_offset_monthly(base, 1) == datetime(2025, 2, 15)
        assert apply_offset_monthly(base, -1) == datetime(2024, 12, 15)
        assert apply_offset_monthly(base, 6) == datetime(2025, 7, 15)
        assert apply_offset_monthly(base, 12) == datetime(2026, 1, 15)

    def test_apply_offset_monthly_edge_cases(self) -> None:
        """Test monthly offset with edge cases (month-end dates)."""
        # Jan 31 → Feb 28/29
        base = datetime(2025, 1, 31)
        assert apply_offset_monthly(base, 1) == datetime(2025, 2, 28)

        base_leap = datetime(2024, 1, 31)
        assert apply_offset_monthly(base_leap, 1) == datetime(2024, 2, 29)

        # Mar 31 → Apr 30
        base = datetime(2025, 3, 31)
        assert apply_offset_monthly(base, 1) == datetime(2025, 4, 30)

    def test_apply_offset_quarterly(self) -> None:
        """Test quarterly offset application."""
        base = datetime(2025, 1, 15)
        assert apply_offset_quarterly(base, 0) == datetime(2025, 1, 15)
        assert apply_offset_quarterly(base, 1) == datetime(2025, 4, 15)
        assert apply_offset_quarterly(base, -1) == datetime(2024, 10, 15)
        assert apply_offset_quarterly(base, 4) == datetime(2026, 1, 15)

    def test_apply_offset_yearly(self) -> None:
        """Test yearly offset application."""
        base = datetime(2025, 1, 15)
        assert apply_offset_yearly(base, 0) == datetime(2025, 1, 15)
        assert apply_offset_yearly(base, 1) == datetime(2026, 1, 15)
        assert apply_offset_yearly(base, -1) == datetime(2024, 1, 15)
        assert apply_offset_yearly(base, 10) == datetime(2035, 1, 15)

    def test_apply_offset_yearly_leap_year(self) -> None:
        """Test yearly offset with leap year edge case (Feb 29)."""
        # Feb 29 2024 (leap) → Feb 28 2025 (non-leap)
        base = datetime(2024, 2, 29)
        assert apply_offset_yearly(base, 1) == datetime(2025, 2, 28)

        # Feb 29 2024 → Feb 29 2028 (both leap)
        assert apply_offset_yearly(base, 4) == datetime(2028, 2, 29)
