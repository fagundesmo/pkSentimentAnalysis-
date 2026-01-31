"""Scrape Reddit public JSON endpoints — no API key required."""

import time
from datetime import datetime

import requests

from config import SUBREDDITS, MAX_RESULTS_PER_QUERY

HEADERS = {
    "User-Agent": "pokemon-sentiment-scraper/1.0"
}


def _fetch_subreddit_search(subreddit: str, query: str, limit: int = 25) -> list[dict]:
    """Search a subreddit using the public JSON API."""
    url = f"https://old.reddit.com/r/{subreddit}/search.json"
    params = {
        "q": query,
        "restrict_sr": "on",
        "sort": "relevance",
        "t": "month",
        "limit": min(limit, 100),
    }
    results = []
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        for post in data.get("data", {}).get("children", []):
            p = post["data"]
            title = p.get("title", "")
            selftext = p.get("selftext", "")
            text = f"{title}. {selftext}".strip()
            created = datetime.fromtimestamp(p.get("created_utc", 0)).isoformat()

            results.append({
                "source": "reddit_public",
                "query": query,
                "title": title,
                "text": text,
                "score": p.get("score", 0),
                "date": created,
                "url": f"https://reddit.com{p.get('permalink', '')}",
            })
    except Exception as e:
        print(f"[reddit_public] Error for r/{subreddit} query '{query}': {e}")

    return results


def scrape_reddit_public(queries: list[str]) -> list[dict]:
    """Scrape Reddit using public JSON endpoints (no API key needed).

    Returns a list of dicts with keys: source, query, title, text, score, date, url.
    """
    results = []
    for subreddit in SUBREDDITS:
        for query in queries:
            results.extend(_fetch_subreddit_search(subreddit, query))
            time.sleep(2)  # respect rate limits

    print(f"[reddit_public] Scraped {len(results)} items")
    return results
