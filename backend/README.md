# Backend: Buffett MVP Scoring Engine

FastAPI-based scoring engine that evaluates stocks using Buffett's investment checklist (5 weighted categories).

## Quick Start

### Prerequisites
- **Python**: 3.11+ (check with `python3 --version`)
- **pip**: Python package manager

### Installation

```bash
cd backend

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS / Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python3 -m pip list | grep fastapi
```

### Start Server

```bash
# Make sure venv is activated
source venv/bin/activate  # macOS/Linux

# Start FastAPI server (with auto-reload)
uvicorn main:app --reload

# Server runs on http://localhost:8000
```

## Project Structure

```
backend/
├── main.py                # FastAPI app + 6 routes
├── scorer.py              # 5-category scoring logic
├── services.py            # Data orchestration (fetch/score/cache)
├── data_collector.py      # yfinance integration
├── watchlist_loader.py    # Load stocks from YAML
├── models.py              # Pydantic models (Stock, StockEvaluation)
├── watchlist.yaml         # Stock ticker list
├── requirements.txt       # Python dependencies
├── data/                  # JSON cache (auto-created)
└── README.md              # This file
```

## API Endpoints

### Health & Metadata

```bash
# Health check
curl http://localhost:8000/api/health
# Response: {"status": "ok"}

# Get watchlist (all tracked stocks)
curl http://localhost:8000/api/watchlist
# Response: list of stocks with ticker, name, sector
```

### Stock Rankings & Evaluations

```bash
# Get all stocks with evaluations (sorted by score descending)
curl http://localhost:8000/api/stocks
# Response: list of StockEvaluation objects

# Get single stock evaluation
curl http://localhost:8000/api/stocks/MSFT
# Response: StockEvaluation with financials, scores, judgment
```

### Refresh Data

```bash
# Force refresh all stock data (fetches from yfinance, ignores cache)
curl -X POST http://localhost:8000/api/stocks/refresh-all
# Response: {"status": "completed", "updated": 6, "failed": 0, "errors": []}

# Force refresh single stock
curl -X POST http://localhost:8000/api/stocks/MSFT/refresh
# Response: StockEvaluation object

# Reload watchlist from YAML
curl -X POST http://localhost:8000/api/watchlist/reload
# Response: {"status": "reloaded", "count": 6}
```

## Scoring System

### 5 Categories

| Category | Weight | Logic | Score Range |
|----------|--------|-------|------------|
| **Business** | 15% | Revenue CAGR (5-year) | 0–100 |
| **Moat** | 25% | Average ROE (all years) | 0–100 |
| **Management** | 15% | EPS growth vs. share buybacks | 0–100 |
| **Financial** | 20% | Equity ratio + Debt/EBITDA | 0–100 |
| **Value** | 25% | Current P/E vs. 5-year avg P/E | 0–100 |

**Total Score** = weighted sum of 5 categories (0–100)

### Judgment Classification

- **BUY**: total_score ≥ 75
- **WATCH**: total_score 55–74
- **PASS**: total_score < 55

### Score Details

Each category returns raw metrics in `details` dict:

```typescript
// Example: Business score
{
  "score": 85.0,
  "details": {
    "revenue_cagr_5y": 0.082,      // 8.2% CAGR
    "data_points": 5,               // Years of data
    "revenue_start": 1000000000,   // Starting revenue
    "revenue_end": 1150000000      // Ending revenue
  }
}
```

See [scorer.py](scorer.py) for all detail fields.

## Data Pipeline

```
yfinance → fetch_stock_data() → save to JSON cache → scorer → StockEvaluation
                                      ↑
                    is_fresh()? (24h TTL)
                         Yes ↓ skip fetch
```

### Cache Strategy

- **Location**: `backend/data/{ticker}.json`
- **TTL**: 24 hours
- **Check**: `_is_fresh()` in services.py

### Cache Invalidation

- Manual: `curl -X POST http://localhost:8000/api/stocks/refresh-all`
- Age: Auto-refreshed if > 24 hours old
- On-demand: `POST /api/stocks/{ticker}/refresh`

## File Descriptions

### main.py
FastAPI app with 6 routes:
- `GET /api/health` — health check
- `GET /api/watchlist` — list of tracked stocks
- `POST /api/watchlist/reload` — reload from YAML
- `GET /api/stocks` — all evaluations
- `GET /api/stocks/{ticker}` — single evaluation
- `POST /api/stocks/{ticker}/refresh` — force refresh
- `POST /api/stocks/refresh-all` — batch refresh

### scorer.py
5 scoring functions + helper utilities:
- `calculate_business_score()` — revenue CAGR
- `calculate_moat_score()` — ROE
- `calculate_management_score()` — EPS growth & buybacks
- `calculate_financial_score()` — equity ratio & debt
- `calculate_value_score()` — P/E valuation
- `calculate_total_score()` — weighted average
- `get_judgment()` — buy/watch/pass classification
- Helpers: `_filter_valid()`, `_cagr()`

### services.py
Data orchestration layer:
- `_is_fresh()` — check 24h cache TTL
- `_build_evaluation()` — raw data → StockEvaluation
- `get_stock_evaluation()` — fetch (with cache) + score
- `refresh_stock()` — force fetch + score
- `get_all_evaluations()` — batch process tickers

### data_collector.py
yfinance integration:
- `fetch_stock_data()` — download financials from Yahoo
- `load_stock_data()` — read JSON cache
- `save_stock_data()` — write JSON cache

### watchlist_loader.py
YAML loading:
- `get_watchlist()` — returns list of tickers
- `load_watchlist()` — parse watchlist.yaml

### models.py
Pydantic v1 models:
- `FinancialData` — fiscal_year, revenue, eps, etc.
- `CategoryScore` — score + details dict
- `Stock` — ticker, name, sector, price
- `StockEvaluation` — full evaluation with scores

## Dependencies

```
fastapi==0.104+      # Web framework
uvicorn==0.24+       # ASGI server
pydantic==1.10+      # Data validation
pyyaml==6.0+         # YAML parsing
yfinance==0.2.4+     # Yahoo Finance API
pandas==2.1+         # Data manipulation
```

See `requirements.txt` for pinned versions.

## Common Tasks

### Add New Stock to Watchlist

1. Edit `watchlist.yaml`:
```yaml
stocks:
  - ticker: NVDA
    name: NVIDIA Corporation
    sector: Technology
```

2. Reload:
```bash
curl -X POST http://localhost:8000/api/watchlist/reload
```

3. Fetch data:
```bash
curl -X POST http://localhost:8000/api/stocks/refresh-all
```

### Test Single Stock

```bash
python3 data_collector.py MSFT
# → downloads MSFT data and displays it

# Or via API:
curl http://localhost:8000/api/stocks/MSFT | python3 -m json.tool
```

### Debug Scoring

```python
# In Python REPL:
from data_collector import fetch_stock_data, load_stock_data
from scorer import calculate_business_score
import json

data = load_stock_data('MSFT')
financials = [FinancialData(**f) for f in data['financials']]
score = calculate_business_score(financials)
print(json.dumps(score.dict(), indent=2))
```

### Check Cache Age

```bash
ls -la backend/data/
# → see modification times of cached JSON files

# Or check API:
curl http://localhost:8000/api/stocks/MSFT | python3 -c "
import json, sys
data = json.load(sys.stdin)
print('Last updated:', data['stock']['last_updated'])
"
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'fastapi'"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Port 8000 already in use"
```bash
# Use different port
uvicorn main:app --reload --port 8001

# Or kill existing process
lsof -ti:8000 | xargs kill -9
```

### yfinance Connection Errors
- Check internet connection
- yfinance may have rate limits (wait a minute)
- Try manually: `python3 data_collector.py TICKER`

### Empty or Missing Financial Data
- Some stocks may lack 5 years of history
- Check cache: `cat backend/data/{ticker}.json | python3 -m json.tool`
- Scoring returns score=50 (neutral) with error details if insufficient data

### Score Validation Errors
- Ensure all scores are 0–100: `curl http://localhost:8000/api/stocks | python3 -m json.tool | grep "total_score"`
- Check scorer logic for division by zero (should be guarded)

## Performance Notes

- **First load**: 30–60s (yfinance fetches + scoring)
- **Cached load**: <100ms (scores already computed)
- **Cache refresh**: 15–30s per stock

## Full Setup Instructions

See root [README.md](../README.md) for backend + frontend setup.
