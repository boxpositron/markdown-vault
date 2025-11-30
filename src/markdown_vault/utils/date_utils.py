"""
Date formatting utilities for periodic notes.

This module provides date formatting functions for different periodic note types:
- Daily: YYYY-MM-DD
- Weekly: YYYY-[W]WW
- Monthly: YYYY-MM
- Quarterly: YYYY-[Q]Q
- Yearly: YYYY

Also includes utilities for parsing date offsets like "+1", "-2", "today".
"""

from datetime import datetime, timedelta


def format_daily(date: datetime) -> str:
    """
    Format a date for daily notes.

    Args:
        date: The date to format

    Returns:
        Formatted date string in YYYY-MM-DD format

    Examples:
        >>> format_daily(datetime(2025, 1, 15))
        '2025-01-15'
    """
    return date.strftime("%Y-%m-%d")


def format_weekly(date: datetime) -> str:
    """
    Format a date for weekly notes.

    Uses ISO week numbers (W01-W53).

    Args:
        date: The date to format

    Returns:
        Formatted date string in YYYY-[W]WW format

    Examples:
        >>> format_weekly(datetime(2025, 1, 15))
        '2025-W03'
    """
    iso_year, iso_week, _ = date.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def format_monthly(date: datetime) -> str:
    """
    Format a date for monthly notes.

    Args:
        date: The date to format

    Returns:
        Formatted date string in YYYY-MM format

    Examples:
        >>> format_monthly(datetime(2025, 1, 15))
        '2025-01'
    """
    return date.strftime("%Y-%m")


def format_quarterly(date: datetime) -> str:
    """
    Format a date for quarterly notes.

    Quarters:
    - Q1: Jan-Mar
    - Q2: Apr-Jun
    - Q3: Jul-Sep
    - Q4: Oct-Dec

    Args:
        date: The date to format

    Returns:
        Formatted date string in YYYY-[Q]Q format

    Examples:
        >>> format_quarterly(datetime(2025, 1, 15))
        '2025-Q1'
        >>> format_quarterly(datetime(2025, 7, 1))
        '2025-Q3'
    """
    quarter = (date.month - 1) // 3 + 1
    return f"{date.year}-Q{quarter}"


def format_yearly(date: datetime) -> str:
    """
    Format a date for yearly notes.

    Args:
        date: The date to format

    Returns:
        Formatted date string in YYYY format

    Examples:
        >>> format_yearly(datetime(2025, 1, 15))
        '2025'
    """
    return str(date.year)


def parse_period_offset(offset: str) -> int:
    """
    Parse a period offset string into an integer.

    Supported formats:
    - "today" or "0" → 0
    - "+N" → N (positive offset)
    - "-N" → -N (negative offset)
    - "N" → N (assume positive)

    Args:
        offset: Offset string to parse

    Returns:
        Integer offset value

    Raises:
        ValueError: If offset format is invalid

    Examples:
        >>> parse_period_offset("today")
        0
        >>> parse_period_offset("+1")
        1
        >>> parse_period_offset("-2")
        -2
        >>> parse_period_offset("3")
        3
    """
    offset = offset.strip()

    # Handle special case
    if offset.lower() == "today":
        return 0

    # Handle numeric offsets
    try:
        # Try parsing as integer (handles +N, -N, and N)
        return int(offset)
    except ValueError:
        raise ValueError(
            f"Invalid offset format: {offset}. "
            f"Expected 'today', '0', '+N', '-N', or 'N'"
        )


def apply_offset_daily(base_date: datetime, offset: int) -> datetime:
    """
    Apply a day offset to a date.

    Args:
        base_date: Base date to offset from
        offset: Number of days to offset (positive or negative)

    Returns:
        Offset date

    Examples:
        >>> apply_offset_daily(datetime(2025, 1, 15), 1)
        datetime.datetime(2025, 1, 16, 0, 0)
        >>> apply_offset_daily(datetime(2025, 1, 15), -7)
        datetime.datetime(2025, 1, 8, 0, 0)
    """
    return base_date + timedelta(days=offset)


def apply_offset_weekly(base_date: datetime, offset: int) -> datetime:
    """
    Apply a week offset to a date.

    Args:
        base_date: Base date to offset from
        offset: Number of weeks to offset (positive or negative)

    Returns:
        Offset date

    Examples:
        >>> apply_offset_weekly(datetime(2025, 1, 15), 1)
        datetime.datetime(2025, 1, 22, 0, 0)
    """
    return base_date + timedelta(weeks=offset)


def apply_offset_monthly(base_date: datetime, offset: int) -> datetime:
    """
    Apply a month offset to a date.

    Handles edge cases like month-end dates properly.

    Args:
        base_date: Base date to offset from
        offset: Number of months to offset (positive or negative)

    Returns:
        Offset date

    Examples:
        >>> apply_offset_monthly(datetime(2025, 1, 15), 1)
        datetime.datetime(2025, 2, 15, 0, 0)
        >>> apply_offset_monthly(datetime(2025, 1, 31), 1)
        datetime.datetime(2025, 2, 28, 0, 0)
    """
    # Calculate target month and year
    target_month = base_date.month + offset
    target_year = base_date.year

    # Handle month overflow/underflow
    while target_month > 12:
        target_month -= 12
        target_year += 1
    while target_month < 1:
        target_month += 12
        target_year -= 1

    # Handle day overflow (e.g., Jan 31 → Feb 28/29)
    import calendar

    max_day = calendar.monthrange(target_year, target_month)[1]
    target_day = min(base_date.day, max_day)

    return datetime(target_year, target_month, target_day)


def apply_offset_quarterly(base_date: datetime, offset: int) -> datetime:
    """
    Apply a quarter offset to a date.

    A quarter is 3 months.

    Args:
        base_date: Base date to offset from
        offset: Number of quarters to offset (positive or negative)

    Returns:
        Offset date

    Examples:
        >>> apply_offset_quarterly(datetime(2025, 1, 15), 1)
        datetime.datetime(2025, 4, 15, 0, 0)
    """
    return apply_offset_monthly(base_date, offset * 3)


def apply_offset_yearly(base_date: datetime, offset: int) -> datetime:
    """
    Apply a year offset to a date.

    Handles leap year edge cases (Feb 29).

    Args:
        base_date: Base date to offset from
        offset: Number of years to offset (positive or negative)

    Returns:
        Offset date

    Examples:
        >>> apply_offset_yearly(datetime(2025, 1, 15), 1)
        datetime.datetime(2026, 1, 15, 0, 0)
    """
    target_year = base_date.year + offset

    # Handle Feb 29 on non-leap years
    if base_date.month == 2 and base_date.day == 29:
        import calendar

        if not calendar.isleap(target_year):
            return datetime(target_year, 2, 28)

    return datetime(target_year, base_date.month, base_date.day)


__all__ = [
    "apply_offset_daily",
    "apply_offset_monthly",
    "apply_offset_quarterly",
    "apply_offset_weekly",
    "apply_offset_yearly",
    "format_daily",
    "format_monthly",
    "format_quarterly",
    "format_weekly",
    "format_yearly",
    "parse_period_offset",
]
