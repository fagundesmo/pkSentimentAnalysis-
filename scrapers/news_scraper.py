"""Scrape Google News results and article snippets for Pokemon card topics."""

import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from config import MAX_RESULTS_PER_QUERY

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


def _search_google_news(query: str, num_results: int = 20) -> list[dict]:
    """Fetch Google News search results for a query."""
    url = "https://www.google.com/search"
    params = {"q": query, "tbm": "nws", "num": num_results, "hl": "en"}

    results = []
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for item in soup.select("div.SoaBEf"):
            title_el = item.select_one("div.MBeuO")
            snippet_el = item.select_one("div.GI74Re")
            link_el = item.select_one("a")
            date_el = item.select_one("span.r0bn4c")

            title = title_el.get_text(strip=True) if title_el else ""
            snippet = snippet_el.get_text(strip=True) if snippet_el else ""
            link = link_el["href"] if link_el and link_el.has_attr("href") else ""
            date_str = date_el.get_text(strip=True) if date_el else ""

            if title or snippet:
                results.append({
                    "source": "google_news",
                    "query": query,
                    "title": title,
                    "text": f"{title}. {snippet}",
                    "score": 0,
                    "date": date_str or datetime.now().isoformat(),
                    "url": link,
                })
    except Exception as e:
        print(f"[news] Error for query '{query}': {e}")

    return results


def scrape_news(queries: list[str]) -> list[dict]:
    """Scrape news articles for all queries.

    Returns a list of dicts with keys: source, query, title, text, score, date, url.
    """
    results = []
    for query in queries:
        results.extend(_search_google_news(query, num_results=MAX_RESULTS_PER_QUERY))
        time.sleep(2)  # be polite to Google

    print(f"[news] Scraped {len(results)} items")
    return results
