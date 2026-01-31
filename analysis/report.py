"""Generate visual reports from sentiment analysis results."""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud


OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def print_summary(df: pd.DataFrame):
    """Print a text summary of the sentiment analysis."""
    total = len(df)
    if total == 0:
        print("No data to summarize.")
        return

    counts = df["sentiment"].value_counts()
    print("\n" + "=" * 60)
    print("POKEMON CARD SENTIMENT ANALYSIS REPORT")
    print("=" * 60)
    print(f"Total items analyzed: {total}")
    print(f"  Positive: {counts.get('positive', 0)} ({counts.get('positive', 0)/total*100:.1f}%)")
    print(f"  Neutral:  {counts.get('neutral', 0)} ({counts.get('neutral', 0)/total*100:.1f}%)")
    print(f"  Negative: {counts.get('negative', 0)} ({counts.get('negative', 0)/total*100:.1f}%)")
    print(f"Average polarity:     {df['polarity'].mean():.4f}")
    print(f"Average subjectivity: {df['subjectivity'].mean():.4f}")

    print("\n--- By Source ---")
    for source, group in df.groupby("source"):
        avg = group["polarity"].mean()
        print(f"  {source}: avg polarity={avg:.4f} ({len(group)} items)")

    print("\n--- By Query ---")
    for query, group in df.groupby("query"):
        avg = group["polarity"].mean()
        print(f"  '{query}': avg polarity={avg:.4f} ({len(group)} items)")

    print("\n--- Most Positive ---")
    top = df.nlargest(3, "polarity")
    for _, row in top.iterrows():
        print(f"  [{row['source']}] {row['text'][:100]}... (polarity={row['polarity']})")

    print("\n--- Most Negative ---")
    bottom = df.nsmallest(3, "polarity")
    for _, row in bottom.iterrows():
        print(f"  [{row['source']}] {row['text'][:100]}... (polarity={row['polarity']})")
    print("=" * 60)


def plot_sentiment_distribution(df: pd.DataFrame):
    """Save a bar chart of sentiment distribution."""
    ensure_output_dir()
    counts = df["sentiment"].value_counts()
    colors = {"positive": "#4CAF50", "neutral": "#FFC107", "negative": "#F44336"}

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(counts.index, counts.values, color=[colors.get(s, "#999") for s in counts.index])
    ax.set_title("Pokemon Card Sentiment Distribution")
    ax.set_ylabel("Count")
    for bar, val in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5, str(val), ha="center")

    path = os.path.join(OUTPUT_DIR, "sentiment_distribution.png")
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"Saved: {path}")


def plot_polarity_by_query(df: pd.DataFrame):
    """Save a box plot of polarity scores grouped by search query."""
    ensure_output_dir()
    fig, ax = plt.subplots(figsize=(12, 6))
    df.boxplot(column="polarity", by="query", ax=ax, vert=True)
    ax.set_title("Polarity by Search Query")
    ax.set_xlabel("Query")
    ax.set_ylabel("Polarity")
    plt.suptitle("")
    plt.xticks(rotation=30, ha="right")

    path = os.path.join(OUTPUT_DIR, "polarity_by_query.png")
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"Saved: {path}")


def generate_wordcloud(df: pd.DataFrame):
    """Save a word cloud from all text."""
    ensure_output_dir()
    text = " ".join(df["text"].astype(str).tolist())
    wc = WordCloud(width=1200, height=600, background_color="white", colormap="viridis").generate(text)

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("Pokemon Card Discussion Word Cloud")

    path = os.path.join(OUTPUT_DIR, "wordcloud.png")
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"Saved: {path}")


def save_csv(df: pd.DataFrame):
    """Save the full results to CSV."""
    ensure_output_dir()
    path = os.path.join(OUTPUT_DIR, "sentiment_results.csv")
    df.to_csv(path, index=False)
    print(f"Saved: {path}")
