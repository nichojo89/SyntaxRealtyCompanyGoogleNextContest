from datetime import date, datetime


def parse_mm_dd_yyyy(value: str) -> date:
    """Parses strings int mm/dd/yyyy format"""

    try:
        dt_object = datetime.strptime(value, "%m/%d/%Y")
        return dt_object.date()
    except ValueError:
        raise ValueError(f"Date string does not match format 'mm/dd/yyyy': {value}")