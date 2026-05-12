import yaml
import logging
from pathlib import Path
from models import WatchlistEntry, Watchlist

logger = logging.getLogger(__name__)


def load_watchlist(path: str = "watchlist.yaml") -> Watchlist:
    """
    Load stock watchlist from YAML file.
    Invalid entries are skipped with warning logs.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Watchlist file not found: {path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    entries = []
    seen_tickers = set()

    for item in data.get('stocks', []):
        try:
            entry = WatchlistEntry(**item)
            if entry.ticker in seen_tickers:
                logger.warning(f"Duplicate ticker: {entry.ticker}, skipping")
                continue
            seen_tickers.add(entry.ticker)
            entries.append(entry)
        except Exception as e:
            logger.warning(f"Invalid entry {item}: {e}")
            continue

    return Watchlist(
        version=data.get('version', '1.0'),
        last_updated=data.get('last_updated'),
        stocks=entries
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    wl = load_watchlist()
    print(f"Loaded {len(wl.stocks)} stocks (version {wl.version}):")
    for stock in wl.stocks:
        print(f"  - {stock.ticker:8} ({stock.sector})")
