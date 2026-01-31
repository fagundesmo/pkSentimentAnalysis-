"""Scrape Twitter/X for Pokemon card discussions."""

import os
from datetime import datetime

import tweepy
from dotenv import load_dotenv

from config import MAX_RESULTS_PER_QUERY

load_dotenv()


def scrape_twitter(queries: list[str]) -> list[dict]:
    """Scrape tweets matching the given queries.

    Returns a list of dicts with keys: source, query, title, text, score, date, url.
    """
    auth = tweepy.OAuth1UserHandler(
        os.getenv("TWITTER_API_KEY"),
        os.getenv("TWITTER_API_SECRET"),
        os.getenv("TWITTER_ACCESS_TOKEN"),
        os.getenv("TWITTER_ACCESS_SECRET"),
    )
    api = tweepy.API(auth, wait_on_rate_limit=True)

    results = []

    for query in queries:
        try:
            tweets = tweepy.Cursor(
                api.search_tweets,
                q=f"{query} -filter:retweets",
                lang="en",
                tweet_mode="extended",
            ).items(MAX_RESULTS_PER_QUERY)

            for tweet in tweets:
                results.append({
                    "source": "twitter",
                    "query": query,
                    "title": "",
                    "text": tweet.full_text[:2000],
                    "score": tweet.favorite_count + tweet.retweet_count,
                    "date": tweet.created_at.isoformat(),
                    "url": f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}",
                })
        except Exception as e:
            print(f"[twitter] Error for query '{query}': {e}")

    print(f"[twitter] Scraped {len(results)} items")
    return results
