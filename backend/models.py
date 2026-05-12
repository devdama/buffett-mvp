from pydantic import BaseModel, validator
from datetime import datetime
import re


class WatchlistEntry(BaseModel):
    """A single entry in the watchlist (loaded from YAML)."""
    ticker: str
    sector: str
    # Reserved fields for future expansion (unused in MVP, but accepted)
    priority: str | None = None
    tags: list[str] | None = None
    notes: str | None = None
    added_date: str | None = None
    target_price: float | None = None

    @validator('ticker')
    def validate_ticker(cls, v):
        v = v.strip().upper()
        if not re.match(r'^[A-Z0-9.\-]{1,10}$', v):
            raise ValueError(f"Invalid ticker format: {v}")
        return v

    @validator('sector')
    def validate_sector(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Sector cannot be empty")
        return v

    class Config:
        extra = "allow"


class Watchlist(BaseModel):
    """Complete watchlist structure."""
    version: str = "1.0"
    last_updated: str | None = None
    stocks: list[WatchlistEntry]


class Stock(BaseModel):
    """Basic stock information."""
    ticker: str
    name: str
    sector: str
    current_price: float
    last_updated: datetime


class FinancialData(BaseModel):
    """Annual financial data for a single fiscal year."""
    fiscal_year: int
    revenue: float
    operating_income: float
    net_income: float
    eps: float
    shares_outstanding: float
    total_assets: float
    total_equity: float
    total_debt: float
    operating_cash_flow: float
    free_cash_flow: float


class CategoryScore(BaseModel):
    """Score for a single evaluation category."""
    score: float  # 0-100
    details: dict


class StockEvaluation(BaseModel):
    """Complete evaluation result for a stock."""
    stock: Stock
    financials: list[FinancialData]
    scores: dict
    total_score: float
    judgment: str  # "buy" | "watch" | "pass"
