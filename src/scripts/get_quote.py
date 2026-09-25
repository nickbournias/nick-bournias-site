import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

QUOTES_PATH = os.path.join(PROJECT_ROOT, "src", "data", "quotes.json")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "public", "daily-quote.json")

START_DATE = datetime(2026, 1, 1, tzinfo=ZoneInfo("America/Denver")).date()


def main():
    with open(QUOTES_PATH, "r", encoding="utf-8") as f:
        quotes = json.load(f)

    today = datetime.now(ZoneInfo("America/Denver")).date()

    days_since_start = (today - START_DATE).days
    quote_index = days_since_start % len(quotes)

    selected = quotes[quote_index]

    output = {
        "date": today.isoformat(),
        "quote": selected["quote"],
        "author": selected["author"],
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(
        f'Saved daily quote for {today}: '
        f'"{selected["quote"]}" — {selected["author"]}'
    )


if __name__ == "__main__":
    main()
