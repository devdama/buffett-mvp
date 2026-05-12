import logging
from models import FinancialData, CategoryScore

logger = logging.getLogger(__name__)


def _filter_valid(financials: list[FinancialData]) -> list[FinancialData]:
    return [f for f in financials if not (f.revenue == 0.0 and f.total_assets == 0.0)]


def _cagr(start: float, end: float, years: int) -> float | None:
    if start <= 0 or years <= 0:
        return None
    return (end / start) ** (1 / years) - 1


def calculate_business_score(financials: list[FinancialData]) -> CategoryScore:
    valid = _filter_valid(financials)
    if len(valid) < 2:
        return CategoryScore(
            score=50.0,
            details={"error": "insufficient data", "data_points": len(valid)},
        )

    revenue_start = valid[0].revenue
    revenue_end = valid[-1].revenue
    year_gap = valid[-1].fiscal_year - valid[0].fiscal_year

    cagr_val = _cagr(revenue_start, revenue_end, year_gap)
    if cagr_val is None:
        score = 0.0
    elif cagr_val >= 0.10:
        score = 100.0
    elif cagr_val >= 0.05:
        score = 70.0
    elif cagr_val >= 0.0:
        score = 40.0
    else:
        score = 0.0

    return CategoryScore(
        score=score,
        details={
            "revenue_cagr_5y": cagr_val,
            "data_points": len(valid),
            "revenue_start": revenue_start,
            "revenue_end": revenue_end,
            "year_gap": year_gap,
        },
    )


def calculate_moat_score(financials: list[FinancialData]) -> CategoryScore:
    valid = _filter_valid(financials)
    if len(valid) < 2:
        return CategoryScore(
            score=50.0,
            details={"error": "insufficient data", "data_points": len(valid)},
        )

    roe_values = []
    for f in valid:
        if f.total_equity > 0:
            roe = f.net_income / f.total_equity
            roe_values.append(roe)

    if not roe_values:
        return CategoryScore(
            score=50.0,
            details={"error": "no valid equity data", "data_points": len(valid)},
        )

    roe_avg = sum(roe_values) / len(roe_values)

    if roe_avg >= 0.20:
        score = 100.0
    elif roe_avg >= 0.15:
        score = 80.0
    elif roe_avg >= 0.10:
        score = 50.0
    else:
        score = 20.0

    return CategoryScore(
        score=score,
        details={
            "roe_avg": roe_avg,
            "data_points": len(roe_values),
            "roe_values": [round(r, 4) for r in roe_values],
        },
    )


def calculate_management_score(financials: list[FinancialData]) -> CategoryScore:
    valid = _filter_valid(financials)
    if len(valid) < 2:
        return CategoryScore(
            score=50.0,
            details={"error": "insufficient data", "data_points": len(valid)},
        )

    oldest = valid[0]
    newest = valid[-1]

    if oldest.eps <= 0 or oldest.shares_outstanding <= 0:
        return CategoryScore(
            score=50.0,
            details={
                "error": "invalid eps or shares in oldest year",
                "eps_start": oldest.eps,
                "shares_start": oldest.shares_outstanding,
            },
        )

    eps_growth = (newest.eps / oldest.eps) - 1
    shares_change = (newest.shares_outstanding / oldest.shares_outstanding) - 1

    if eps_growth > 0 and shares_change < 0:
        score = 100.0
    elif eps_growth > 0 and shares_change < 0.02:
        score = 80.0
    elif eps_growth > shares_change:
        score = 50.0
    else:
        score = 30.0

    return CategoryScore(
        score=score,
        details={
            "eps_growth": round(eps_growth, 4),
            "shares_change": round(shares_change, 4),
            "eps_start": round(oldest.eps, 4),
            "eps_end": round(newest.eps, 4),
            "shares_start": round(oldest.shares_outstanding, 0),
            "shares_end": round(newest.shares_outstanding, 0),
        },
    )


def calculate_financial_score(financials: list[FinancialData]) -> CategoryScore:
    valid = _filter_valid(financials)
    if not valid:
        return CategoryScore(
            score=50.0,
            details={"error": "no valid financial data"},
        )

    most_recent = valid[-1]

    if most_recent.total_assets <= 0:
        equity_score = 20.0
        equity_ratio = 0.0
    else:
        equity_ratio = most_recent.total_equity / most_recent.total_assets
        if equity_ratio >= 0.50:
            equity_score = 100.0
        elif equity_ratio >= 0.40:
            equity_score = 80.0
        elif equity_ratio >= 0.30:
            equity_score = 50.0
        else:
            equity_score = 20.0

    if most_recent.operating_income <= 0 and most_recent.total_debt == 0:
        debt_ebitda = 0.0
        debt_score = 100.0
    elif most_recent.operating_income > 0:
        debt_ebitda = most_recent.total_debt / most_recent.operating_income
        if debt_ebitda <= 1.0:
            debt_score = 100.0
        elif debt_ebitda <= 2.0:
            debt_score = 80.0
        elif debt_ebitda <= 3.0:
            debt_score = 50.0
        else:
            debt_score = 20.0
    else:
        debt_ebitda = float('inf') if most_recent.total_debt > 0 else 0.0
        debt_score = 20.0 if most_recent.total_debt > 0 else 100.0

    final_score = (equity_score + debt_score) / 2

    return CategoryScore(
        score=final_score,
        details={
            "equity_ratio": round(equity_ratio, 4),
            "equity_score": equity_score,
            "debt_ebitda": round(debt_ebitda, 4) if debt_ebitda != float('inf') else None,
            "debt_score": debt_score,
            "total_equity": most_recent.total_equity,
            "total_assets": most_recent.total_assets,
            "total_debt": most_recent.total_debt,
            "ebitda_proxy": most_recent.operating_income,
        },
    )


def calculate_value_score(
    current_price: float,
    financials: list[FinancialData],
    trailing_pe: float | None,
) -> CategoryScore:
    valid = _filter_valid(financials)
    if not valid or current_price <= 0:
        return CategoryScore(
            score=50.0,
            details={"error": "missing price or financial data"},
        )

    if trailing_pe is not None and trailing_pe > 0:
        current_pe = trailing_pe
        trailing_pe_source = "yfinance"
    else:
        latest_eps = valid[-1].eps
        if latest_eps <= 0:
            return CategoryScore(
                score=50.0,
                details={"error": "zero or negative latest eps"},
            )
        current_pe = current_price / latest_eps
        trailing_pe_source = "calculated"

    pe_values = []
    for f in valid:
        if f.eps > 0:
            pe = current_price / f.eps
            pe_values.append(pe)

    if not pe_values:
        return CategoryScore(
            score=50.0,
            details={"error": "no valid eps data for pe calculation"},
        )

    avg_pe = sum(pe_values) / len(pe_values)

    if current_pe <= avg_pe * 0.70:
        score = 100.0
    elif current_pe <= avg_pe * 0.85:
        score = 70.0
    elif current_pe <= avg_pe * 1.15:
        score = 50.0
    else:
        score = 20.0

    return CategoryScore(
        score=score,
        details={
            "current_pe": round(current_pe, 2),
            "avg_pe_5y": round(avg_pe, 2),
            "current_price": current_price,
            "trailing_pe_source": trailing_pe_source,
            "data_points": len(pe_values),
        },
    )


def calculate_total_score(scores: dict[str, CategoryScore]) -> float:
    weights = {
        "business": 0.15,
        "moat": 0.25,
        "management": 0.15,
        "financial": 0.20,
        "value": 0.25,
    }

    total = 0.0
    for category, weight in weights.items():
        if category in scores:
            score_obj = scores[category]
            if isinstance(score_obj, CategoryScore):
                score_val = score_obj.score
            else:
                score_val = score_obj.get("score", 0.0)
            total += score_val * weight

    return total


def get_judgment(total_score: float) -> str:
    if total_score >= 75:
        return "buy"
    elif total_score >= 55:
        return "watch"
    else:
        return "pass"
