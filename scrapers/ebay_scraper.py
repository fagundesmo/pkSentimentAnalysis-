"""Scrape eBay sold/completed listings for Pokemon card price sentiment."""

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


def _search_ebay(query: str, num_results: int = 50) -> list[dict]:
    """Fetch eBay sold listings for a query."""
    url = "https://www.ebay.com/sch/i.html"
    params = {
        "_nkw": query,
        "LH_Complete": "1",   # completed listings
        "LH_Sold": "1",       # sold items
        "_ipg": min(num_results, 240),
    }
    results = []
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for item in soup.select("div.s-item__wrapper"):
            title_el = item.select_one("div.s-item__title span")
            price_el = item.select_one("span.s-item__price")
            link_el = item.select_one("a.s-item__link")

            title = title_el.get_text(strip=True) if title_el else ""
            price = price_el.get_text(strip=True) if price_el else ""
            link = link_el["href"] if link_el and link_el.has_attr("href") else ""

            if title and "Shop on eBay" not in title:
                text = f"{title} sold for {price}" if price else title
                results.append({
                    "source": "ebay",
                    "query": query,
                    "title": title,
                    "text": text,
                    "score": 0,
                    "date": datetime.now().isoformat(),
                    "url": link,
                })
    except Exception as e:
        print(f"[ebay] Error for query '{query}': {e}")

    return results


def scrape_ebay(queries: list[str]) -> list[dict]:
    """Scrape eBay sold listings for all queries.

    Returns a list of dicts with keys: source, query, title, text, score, date, url.
    """
    results = []
    for query in queries:
        results.extend(_search_ebay(query, num_results=MAX_RESULTS_PER_QUERY))
        time.sleep(2)

    print(f"[ebay] Scraped {len(results)} items")
    return results
