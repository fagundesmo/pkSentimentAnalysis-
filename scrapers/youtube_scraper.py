"""Scrape YouTube search results for Pokemon card video titles and descriptions."""

import time
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from config import MAX_RESULTS_PER_QUERY

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def _search_youtube(query: str) -> list[dict]:
    """Fetch YouTube search results for a query by parsing the HTML page."""
    url = "https://www.youtube.com/results"
    params = {"search_query": query}
    results = []
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()

        # YouTube embeds video data in a JSON blob inside the HTML
        # Look for the ytInitialData variable
        match = re.search(r"var ytInitialData\s*=\s*({.+?});</script>", resp.text)
        if not match:
            # Alternate pattern
            match = re.search(r"ytInitialData\s*=\s*({.+?});\s*</script>", resp.text)
        if not match:
            print(f"[youtube] Could not parse page for query '{query}'")
            return results

        import json
        data = json.loads(match.group(1))

        # Navigate the nested structure to find video renderers
        contents = (
            data.get("contents", {})
            .get("twoColumnSearchResultsRenderer", {})
            .get("primaryContents", {})
            .get("sectionListRenderer", {})
            .get("contents", [])
        )

        for section in contents:
            items = (
                section.get("itemSectionRenderer", {})
                .get("contents", [])
            )
            for item in items:
                video = item.get("videoRenderer", {})
                if not video:
                    continue

                title_runs = video.get("title", {}).get("runs", [])
                title = "".join(r.get("text", "") for r in title_runs)

                snippet_runs = video.get("detailedMetadataSnippets", [{}])
                snippet = ""
                if snippet_runs:
                    snippet_text_runs = snippet_runs[0].get("snippetText", {}).get("runs", [])
                    snippet = "".join(r.get("text", "") for r in snippet_text_runs)

                video_id = video.get("videoId", "")
                view_count_text = video.get("viewCountText", {}).get("simpleText", "")
                published = video.get("publishedTimeText", {}).get("simpleText", "")

                if title:
                    text = f"{title}. {snippet}".strip() if snippet else title
                    results.append({
                        "source": "youtube",
                        "query": query,
                        "title": title,
                        "text": text,
                        "score": 0,
                        "date": published or datetime.now().isoformat(),
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                    })
    except Exception as e:
        print(f"[youtube] Error for query '{query}': {e}")

    return results


def scrape_youtube(queries: list[str]) -> list[dict]:
    """Scrape YouTube search results for all queries.

    Returns a list of dicts with keys: source, query, title, text, score, date, url.
    """
    results = []
    for query in queries:
        results.extend(_search_youtube(query))
        time.sleep(2)

    print(f"[youtube] Scraped {len(results)} items")
    return results
