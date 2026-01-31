"""Search queries and configuration for Pokemon card sentiment scraping."""

SEARCH_QUERIES = [
    "pokemon cards",
    "best pokemon cards",
    "price for pokemon cards",
    "pokemon card value",
    "pokemon card collection",
    "pokemon TCG",
    "pokemon card investing",
    "rare pokemon cards",
    "pokemon card market",
    "pokemon booster box",
]

# Subreddits to scrape
SUBREDDITS = [
    "PokemonTCG",
    "pokemoncards",
    "PokeInvesting",
    "pokemon",
]

# Number of posts/results to fetch per query
MAX_RESULTS_PER_QUERY = 50
