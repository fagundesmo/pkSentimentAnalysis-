#!/usr/bin/env python3
"""Pokemon Card Sentiment Analysis — main entry point.

Usage:
    python main.py --no-api         # scrape all free sources (no API keys needed)
    python main.py --news-only      # quick run with news only
    python main.py                  # scrape all sources (needs API keys for reddit/twitter)
    python main.py --sources ebay youtube news   # pick specific sources
"""

import argparse
import importlib
import sys

from config import SEARCH_QUERIES
from analysis.sentiment import run_analysis
from analysis.report import (
    print_summary,
    plot_sentiment_distribution,
    plot_polarity_by_query,
    generate_wordcloud,
    save_csv,
)

# Lazy imports — only load a scraper when it's actually used
# Sources marked (API) require credentials in .env; the rest are API-free.
SCRAPER_MODULES = {
    "news": ("scrapers.news_scraper", "scrape_news"),
    "reddit_public": ("scrapers.reddit_public_scraper", "scrape_reddit_public"),
    "ebay": ("scrapers.ebay_scraper", "scrape_ebay"),
    "youtube": ("scrapers.youtube_scraper", "scrape_youtube"),
    "reddit": ("scrapers.reddit_scraper", "scrape_reddit"),       # API key
    "twitter": ("scrapers.twitter_scraper", "scrape_twitter"),     # API key
}

# Sources that work without any API keys
FREE_SOURCES = ["news", "reddit_public", "ebay", "youtube"]


def _get_scraper(name: str):
    module_path, func_name = SCRAPER_MODULES[name]
    module = importlib.import_module(module_path)
    return getattr(module, func_name)


def main():
    parser = argparse.ArgumentParser(description="Pokemon Card Sentiment Analysis")
    parser.add_argument(
        "--sources",
        nargs="+",
        choices=list(SCRAPER_MODULES.keys()),
        default=None,
        help="Sources to scrape (default: all)",
    )
    parser.add_argument(
        "--news-only",
        action="store_true",
        help="Only scrape Google News (no API keys required)",
    )
    parser.add_argument(
        "--no-api",
        action="store_true",
        help="Scrape all free sources (news, reddit public, ebay, youtube) — no API keys needed",
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
    elif args.no_api:
        sources = FREE_SOURCES
    elif args.sources:
        sources = args.sources
    else:
        sources = list(SCRAPER_MODULES.keys())

    # --- Scrape ---
    all_data: list[dict] = []
    for name in sources:
        print(f"\nScraping {name}...")
        scraper_fn = _get_scraper(name)
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
