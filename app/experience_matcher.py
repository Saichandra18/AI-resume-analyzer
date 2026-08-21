from datetime import datetime
import re


def _parse_year_range(year_range):
    """Parse an experience year range into start and end years."""

    if not year_range:
        return None

    pattern = (
        r"^\s*(\d{4})\s*[-–]\s*"
        r"(Present|Current|\d{4})\s*$"
    )

    match = re.match(pattern, year_range, re.IGNORECASE)

    if not match:
        return None

    start_year = int(match.group(1))
    end_value = match.group(2)

    if end_value.lower() in {"present", "current"}:
        end_year = datetime.now().year
    else:
        end_year = int(end_value)

    if end_year < start_year:
        return None

    return start_year, end_year


def _calculate_experience_years(year_ranges):
    """Calculate total non-overlapping experience years."""

    if not year_ranges:
        return None

    periods = []

    for year_range in year_ranges:
        parsed = _parse_year_range(year_range)

        if parsed:
            periods.append(parsed)

    if not periods:
        return None

    periods.sort()

    merged_periods = [periods[0]]

    for current_start, current_end in periods[1:]:
        previous_start, previous_end = merged_periods[-1]

        if current_start <= previous_end:
            merged_periods[-1] = (
                previous_start,
                max(previous_end, current_end),
            )
        else:
            merged_periods.append(
                (current_start, current_end)
            )

    total_years = sum(
        end - start
        for start, end in merged_periods
    )

    return total_years


def match_experience(resume_experience, required_experience):
    """Compare resume experience against the JD experience requirement."""

    resume_experience = resume_experience or {}
    required_experience = required_experience or {}

    year_ranges = resume_experience.get("years", [])
    required_years = required_experience.get("min_years")

    candidate_years = _calculate_experience_years(year_ranges)

    if required_years is None:
        return {
            "required_years": None,
            "candidate_years": candidate_years,
            "meets_requirement": True,
        }

    if candidate_years is None:
        return {
            "required_years": required_years,
            "candidate_years": None,
            "meets_requirement": False,
        }

    return {
        "required_years": required_years,
        "candidate_years": candidate_years,
        "meets_requirement": candidate_years >= required_years,
    }