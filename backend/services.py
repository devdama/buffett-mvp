import logging
from datetime import datetime, timedelta
from models import FinancialData, Stock, StockEvaluation, CategoryScore
from data_collector import load_stock_data, fetch_stock_data, save_stock_data
from scorer import (
    calculate_business_score,
    calculate_moat_score,
    calculate_management_score,
    calculate_financial_score,
    calculate_value_score,
    calculate_total_score,
    get_judgment,
)

logger = logging.getLogger(__name__)


def _is_fresh(last_updated_str: str) -> bool:
    try:
        last_updated = datetime.fromisoformat(last_updated_str.replace("Z", "+00:00"))
        now = datetime.now(last_updated.tzinfo)
        return (now - last_updated) < timedelta(hours=24)
    except Exception as e:
        logger.warning(f"Failed to parse last_updated: {e}")
        return False


def _build_evaluation(data: dict) -> StockEvaluation:
    financials = [FinancialData(**f) for f in data["financials"]]
    stock = Stock(
        ticker=data["ticker"],
        name=data["name"],
        sector=data["sector"],
        current_price=data["current_price"],
        last_updated=datetime.fromisoformat(
            data["last_updated"].replace("Z", "+00:00")
        ),
    )

    scores = {
        "business": calculate_business_score(financials),
        "moat": calculate_moat_score(financials),
        "management": calculate_management_score(financials),
        "financial": calculate_financial_score(financials),
        "value": calculate_value_score(
            data["current_price"],
            financials,
            data.get("trailing_pe"),
        ),
    }

    total_score = calculate_total_score(scores)
    judgment = get_judgment(total_score)

    scores_dict = {k: v.dict() for k, v in scores.items()}

    return StockEvaluation(
        stock=stock,
        financials=financials,
        scores=scores_dict,
        total_score=round(total_score, 1),
        judgment=judgment,
    )


def get_stock_evaluation(ticker: str) -> StockEvaluation:
    cached = load_stock_data(ticker)

    if cached is not None and _is_fresh(cached.get("last_updated", "")):
        logger.info(f"Using cached data for {ticker}")
        return _build_evaluation(cached)

    logger.info(f"Fetching fresh data for {ticker}")
    data = fetch_stock_data(ticker)
    save_stock_data(ticker, data)
    return _build_evaluation(data)


def refresh_stock(ticker: str) -> StockEvaluation:
    logger.info(f"Refreshing {ticker}")
    data = fetch_stock_data(ticker)
    save_stock_data(ticker, data)
    return _build_evaluation(data)


def get_all_evaluations(tickers: list[str]) -> list[StockEvaluation]:
    results = []
    for ticker in tickers:
        try:
            eval = get_stock_evaluation(ticker)
            results.append(eval)
        except Exception as e:
            logger.error(f"Failed to evaluate {ticker}: {e}")
    return results
