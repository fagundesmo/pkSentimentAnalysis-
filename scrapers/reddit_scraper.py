"""Scrape Reddit for Pokemon card discussions."""

import os
from datetime import datetime

import praw
from dotenv import load_dotenv

from config import SUBREDDITS, MAX_RESULTS_PER_QUERY

load_dotenv()


def scrape_reddit(queries: list[str]) -> list[dict]:
    """Scrape Reddit posts and comments matching the given queries.

    Returns a list of dicts with keys: source, query, title, text, score, date, url.
    """
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT", "pokemon_sentiment_scraper"),
    )

    results = []

    for query in queries:
        try:
            for submission in reddit.subreddit("+".join(SUBREDDITS)).search(
                query, limit=MAX_RESULTS_PER_QUERY, sort="relevance", time_filter="month"
            ):
                results.append({
                    "source": "reddit",
                    "query": query,
                    "title": submission.title,
                    "text": f"{submission.title}. {submission.selftext}"[:2000],
                    "score": submission.score,
                    "date": datetime.utcfromtimestamp(submission.created_utc).isoformat(),
                    "url": f"https://reddit.com{submission.permalink}",
                })

                # Also grab top-level comments
                submission.comments.replace_more(limit=0)
                for comment in submission.comments[:5]:
                    results.append({
                        "source": "reddit_comment",
                        "query": query,
                        "title": submission.title,
                        "text": comment.body[:2000],
                        "score": comment.score,
                        "date": datetime.utcfromtimestamp(comment.created_utc).isoformat(),
                        "url": f"https://reddit.com{comment.permalink}",
                    })
        except Exception as e:
            print(f"[reddit] Error for query '{query}': {e}")

    print(f"[reddit] Scraped {len(results)} items")
    return results
