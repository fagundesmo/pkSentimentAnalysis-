# Pokemon Card Sentiment Analysis

Scrapes the internet for Pokemon card discussions and runs sentiment analysis to gauge public opinion on pricing, collecting, and investing.

## Sources

| Source | API Key Required | What it scrapes |
|--------|-----------------|-----------------|
| Google News | No | News articles and headlines |
| Reddit | Yes | Posts and comments from r/PokemonTCG, r/pokemoncards, r/PokeInvesting |
| Twitter/X | Yes | Tweets matching search queries |

## Setup

```bash
pip install -r requirements.txt
python -m textblob.download_corpora   # one-time download for TextBlob
```

For Reddit and Twitter, copy `.env.example` to `.env` and fill in your API credentials.

## Usage

```bash
# Quick start — news only, no API keys needed
python main.py --news-only

# All sources (requires Reddit + Twitter credentials in .env)
python main.py

# Pick specific sources
python main.py --sources reddit news

# Custom search queries
python main.py --news-only --queries "pokemon cards" "charizard price"
```

## Output

All results are saved to the `output/` directory:

- `sentiment_results.csv` — full dataset with polarity and subjectivity scores
- `sentiment_distribution.png` — bar chart of positive/neutral/negative counts
- `polarity_by_query.png` — box plot of polarity grouped by search query
- `wordcloud.png` — word cloud of all scraped text

The terminal also prints a summary with breakdowns by source, query, and the most positive/negative items found.

## Search Queries

Default queries (configurable in `config.py`):

- pokemon cards
- best pokemon cards
- price for pokemon cards
- pokemon card value
- pokemon card collection
- pokemon TCG
- pokemon card investing
- rare pokemon cards
- pokemon card market
- pokemon booster box
