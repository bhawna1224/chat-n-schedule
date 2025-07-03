from datetime import datetime
import dateparser
import pytz

def parse_date_string(date_str: str, timezone: str = "UTC") -> datetime:
    print(f"🛠 Parsing '{date_str}' in timezone '{timezone}'")

    tz = pytz.timezone(timezone)

    dt = dateparser.parse(
        date_str,
        settings={
            "TIMEZONE": timezone,
            "TO_TIMEZONE": timezone,
            "RETURN_AS_TIMEZONE_AWARE": True,
            "PREFER_DATES_FROM": "future",
            "RELATIVE_BASE": datetime.now(tz),
        }
    )

    if not dt:
        print("❌ Failed to parse datetime")
        raise ValueError(f"Could not parse date string: {date_str}")

    print(f"✅ Parsed datetime: {dt.isoformat()}")
    return dt


