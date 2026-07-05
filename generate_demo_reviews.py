import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(7)
OUT = Path(__file__).parent / "demo_reviews.csv"
START = date(2026, 2, 1)

PRAISE = {
    "sound quality": [
        "The sound is incredible — deep bass and crystal clear highs.",
        "Audio quality blew me away, easily better than headphones twice the price.",
        "Rich, balanced sound. Music sounds the way it's meant to.",
    ],
    "noise cancellation": [
        "The noise cancelling is fantastic, the office just disappears.",
        "ANC is top notch — can't hear the plane engine at all.",
        "Blocks out my noisy commute completely, love it.",
    ],
    "comfort": [
        "So comfortable I forget I'm wearing them for hours.",
        "The ear cushions are soft and light, no fatigue at all.",
    ],
    "value": [
        "Amazing value for the money, would buy again.",
        "Can't believe the quality at this price point.",
    ],
    "design": [
        "Sleek, premium design and they fold up neatly for travel.",
        "Beautiful build, feels classy and looks great.",
    ],
}
COMPLAINT = {
    "battery life": [
        "Battery drains way faster than advertised, barely gets half a day.",
        "The battery life is a joke now, dies after a few hours.",
        "Charge doesn't last — I have to top it up every single day.",
    ],
    "Bluetooth connection": [
        "Bluetooth keeps dropping every few minutes, so frustrating.",
        "Constant connection drops when my phone is in my pocket.",
        "Pairing is unreliable and the audio cuts out randomly.",
    ],
    "build quality": [
        "The headband started creaking after two weeks, feels cheap.",
        "Hinge feels flimsy, I'm worried it'll snap.",
    ],
    "microphone": [
        "People on calls say I sound muffled and distant.",
        "The mic quality is poor, colleagues can barely hear me.",
    ],
    "comfort": [
        "They clamp too tightly and my ears hurt after an hour.",
    ],
}
MIXED = [
    ("Great sound but the battery life really lets it down.", 3),
    ("Love the noise cancelling, hate the flaky Bluetooth.", 3),
    ("Comfortable and stylish, though the mic could be better.", 3),
    ("Good headphones overall, just wish the battery lasted longer.", 3),
]


def spread_date(i: int, n: int) -> date:
    return START + timedelta(days=int(i / n * 110) + random.randint(0, 3))


def main() -> None:
    rows = []

    def add(text, rating, d):
        rows.append((text, rating, d.isoformat()))

    for k in range(34):
        theme = random.choice(list(PRAISE))
        text = random.choice(PRAISE[theme])
        add(text, random.choice([4, 5, 5]), spread_date(random.randint(0, 100), 100))
    for k in range(18):
        theme = random.choice(["battery life", "battery life", "Bluetooth connection",
                               "Bluetooth connection", "build quality", "microphone", "comfort"])
        text = random.choice(COMPLAINT[theme])
        d = START + timedelta(days=random.randint(48, 72))
        add(text, random.choice([1, 2, 2]), d)
    for text, rating in MIXED * 2:
        add(text, rating, spread_date(random.randint(0, 100), 100))

    rows.sort(key=lambda r: r[2])
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["review_text", "rating", "date"])
        w.writerows(rows)
    print(f"Wrote {len(rows)} reviews to {OUT.name}")


if __name__ == "__main__":
    main()
