#!/usr/bin/env python3
"""Pokemon Card Sentiment Analysis — main entry point.

Usage:
    python main.py                  # scrape all sources
    python main.py --sources reddit news   # pick specific sources
    python main.py --news-only      # quick run with news only (no API keys needed)
"""

import argparse
import sys

from config import SEARCH_QUERIES
from scrapers.reddit_scraper import scrape_reddit
from scrapers.twitter_scraper import scrape_twitter
from scrapers.news_scraper import scrape_news
from analysis.sentiment import run_analysis
from analysis.report import (
    print_summary,
    plot_sentiment_distribution,
    plot_polarity_by_query,
    generate_wordcloud,
    save_csv,
)


SCRAPERS = {
    "reddit": scrape_reddit,
    "twitter": scrape_twitter,
    "news": scrape_news,
}


def main():
    parser = argparse.ArgumentParser(description="Pokemon Card Sentiment Analysis")
    parser.add_argument(
        "--sources",
        nargs="+",
        choices=list(SCRAPERS.keys()),
        default=None,
        help="Sources to scrape (default: all)",
    )
    parser.add_argument(
        "--news-only",
        action="store_true",
        help="Only scrape Google News (no API keys required)",
    )
    parser.add_argument(
        "--queries",
        nargs="+",
        default=None,
        help="Custom search queries (overrides defaults in config.py)",
    )
    args = parser.parse_args()

    queries = args.queries or SEARCH_QUERIES

    if args.news_only:
        sources = ["news"]
    elif args.sources:
        sources = args.sources
    else:
        sources = list(SCRAPERS.keys())

    # --- Scrape ---
    all_data: list[dict] = []
    for name in sources:
        print(f"\nScraping {name}...")
        scraper_fn = SCRAPERS[name]
        all_data.extend(scraper_fn(queries))

    if not all_data:
        print("No data collected. Check your API credentials or try --news-only.")
        sys.exit(1)

    # --- Analyze ---
    print(f"\nAnalyzing sentiment for {len(all_data)} items...")
    df = run_analysis(all_data)

    # --- Report ---
    print_summary(df)
    save_csv(df)
    plot_sentiment_distribution(df)
    plot_polarity_by_query(df)
    generate_wordcloud(df)

    print("\nDone! Check the output/ directory for charts and CSV data.")


if __name__ == "__main__":
    main()
