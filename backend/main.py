from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

from models import Watchlist
from watchlist_loader import load_watchlist
from services import get_stock_evaluation, get_all_evaluations, refresh_stock

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Buffett MVP API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory watchlist cache (loaded at startup)
_watchlist: Watchlist | None = None


def get_watchlist() -> Watchlist:
    global _watchlist
    if _watchlist is None:
        _watchlist = load_watchlist()
    return _watchlist


@app.on_event("startup")
async def startup_event():
    global _watchlist
    try:
        _watchlist = load_watchlist()
        logger.info(f"Watchlist loaded: {len(_watchlist.stocks)} stocks")
    except Exception as e:
        logger.error(f"Failed to load watchlist on startup: {e}")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/watchlist", response_model=Watchlist)
def get_watchlist_endpoint():
    return get_watchlist()


@app.post("/api/watchlist/reload")
def reload_watchlist():
    global _watchlist
    try:
        _watchlist = load_watchlist()
        return {"status": "reloaded", "stock_count": len(_watchlist.stocks)}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stocks")
def get_stocks():
    watchlist = get_watchlist()
    tickers = [s.ticker for s in watchlist.stocks]
    evaluations = get_all_evaluations(tickers)
    evaluations.sort(key=lambda e: e.total_score, reverse=True)
    return evaluations


@app.post("/api/stocks/refresh-all")
def refresh_all_stocks():
    watchlist = get_watchlist()
    tickers = [s.ticker for s in watchlist.stocks]
    updated = 0
    failed = 0
    errors = []

    for ticker in tickers:
        try:
            refresh_stock(ticker)
            updated += 1
        except Exception as e:
            failed += 1
            errors.append({"ticker": ticker, "error": str(e)})
            logger.error(f"Failed to refresh {ticker}: {e}")

    return {
        "status": "completed",
        "updated": updated,
        "failed": failed,
        "errors": errors,
    }


@app.get("/api/stocks/{ticker}")
def get_stock_detail(ticker: str):
    watchlist = get_watchlist()
    tickers_set = {s.ticker for s in watchlist.stocks}

    if ticker.upper() not in tickers_set:
        raise HTTPException(status_code=404, detail=f"Ticker {ticker} not in watchlist")

    try:
        evaluation = get_stock_evaluation(ticker.upper())
        return evaluation
    except Exception as e:
        logger.error(f"Failed to evaluate {ticker}: {e}")
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/api/stocks/{ticker}/refresh")
def refresh_stock_endpoint(ticker: str):
    watchlist = get_watchlist()
    tickers_set = {s.ticker for s in watchlist.stocks}

    if ticker.upper() not in tickers_set:
        raise HTTPException(status_code=404, detail=f"Ticker {ticker} not in watchlist")

    try:
        evaluation = refresh_stock(ticker.upper())
        return evaluation
    except Exception as e:
        logger.error(f"Failed to refresh {ticker}: {e}")
        raise HTTPException(status_code=502, detail=str(e))
