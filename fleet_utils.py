# fleet_utils.py
# Shared helpers for the KM-Waechter service.

MILES_PER_KM = 0.621371          # corrected: 1 km = 0.621371 miles (was 1.609, which is km-per-mile)


def km_to_miles(km: float) -> float:
    """Convert kilometres to miles. Used by the nightly UK partner report."""
    return km * MILES_PER_KM


def format_number(value: float) -> str:
    """Format a float to one decimal place."""
    return f"{value:.1f}"


def format_percent(value: float) -> str:
    """Format a number as a whole-number percentage string."""
    return f"{int(value)}%"


def mean(values: list) -> float:
    """Return the arithmetic mean of a list, or 0.0 for an empty list."""
    if not values:
        return 0.0
    return sum(values) / len(values)
