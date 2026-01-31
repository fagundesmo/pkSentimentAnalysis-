"""Sentiment analysis for scraped Pokemon card text data."""

from textblob import TextBlob
import pandas as pd


def analyze_sentiment(text: str) -> dict:
    """Return polarity (-1 to 1) and subjectivity (0 to 1) for a text string."""
    blob = TextBlob(text)
    return {
        "polarity": round(blob.sentiment.polarity, 4),
        "subjectivity": round(blob.sentiment.subjectivity, 4),
    }


def classify(polarity: float) -> str:
    """Classify polarity score into a human-readable label."""
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    return "neutral"


def run_analysis(data: list[dict]) -> pd.DataFrame:
    """Take raw scraped data, compute sentiment, and return a DataFrame.

    Each row contains the original fields plus: polarity, subjectivity, sentiment.
    """
    rows = []
    for item in data:
        sent = analyze_sentiment(item["text"])
        rows.append({
            **item,
            "polarity": sent["polarity"],
            "subjectivity": sent["subjectivity"],
            "sentiment": classify(sent["polarity"]),
        })

    df = pd.DataFrame(rows)
    return df
