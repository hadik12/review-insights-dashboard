import argparse
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

from dotenv import load_dotenv

import clustering
import dashboard
import sentiment
from llm import QuotaExhaustedError, make_client


def read_reviews(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if (r.get("review_text") or "").strip()]
    if not rows:
        sys.exit(f"No reviews found in {path}")
    return rows


def monthly_positive(reviews: list[dict], sentiments: list[str]) -> list[tuple]:
    buckets: dict[str, Counter] = defaultdict(Counter)
    for r, s in zip(reviews, sentiments):
        month = (r.get("date") or "")[:7] or "unknown"
        buckets[month][s] += 1
    out = []
    for month in sorted(buckets):
        c = buckets[month]
        total = sum(c.values())
        out.append((month, c["positive"] / total if total else 0, total))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze product reviews into a Plotly dashboard.")
    parser.add_argument("--input", default="demo_reviews.csv", help="reviews CSV (review_text, rating, date)")
    parser.add_argument("--output", default="review_dashboard.html", help="HTML dashboard output")
    parser.add_argument("--product", default="Aurora X2 Wireless Headphones", help="product name for the title")
    args = parser.parse_args()

    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    in_path = Path(args.input)
    if not in_path.is_file():
        sys.exit(f"Error: '{in_path}' not found (run generate_demo_reviews.py first)")

    load_dotenv()
    client = make_client()
    reviews = read_reviews(in_path)
    texts = [r["review_text"].strip() for r in reviews]
    print(f"Loaded {len(texts)} reviews.")

    try:
        print("Scoring sentiment (batched)...")
        sentiments = sentiment.analyze(client, texts)
        print("Clustering themes...")
        report = clustering.extract_themes(client, texts)
    except QuotaExhaustedError as err:
        sys.exit(f"[STOP] {err}")

    counts = Counter(sentiments)
    timeseries = monthly_positive(reviews, sentiments)
    out_path = Path(args.output)
    dashboard.build(args.product, dict(counts), timeseries, report, out_path)

    total = len(texts)
    print(f"\nSentiment: "
          f"{counts['positive']} positive / {counts['negative']} negative / {counts['neutral']} neutral")
    print("Top complaints:")
    for t in report.top_complaints[:3]:
        print(f"  - {t.theme} ({t.mention_count})")
    print("Top praises:")
    for t in report.top_praises[:3]:
        print(f"  - {t.theme} ({t.mention_count})")
    print(f"\nDashboard written to {out_path}")


if __name__ == "__main__":
    main()
