# Buffett-Style Checklist Ranking System - MVP Specification v0.2

## Overview

A web application that evaluates US-listed companies across 5 categories based on Warren Buffett's investment philosophy and displays them in a ranking. The MVP focuses on building a minimal working prototype, with planned incremental expansion.

**v0.2 Changes**: Stock list has been externalized to a YAML file, allowing additions and modifications without code changes.

---

## MVP Goals

- Build a **minimal working prototype** in 1-2 days
- Achieve end-to-end functionality: Load watchlist from YAML → Fetch financial data → Calculate scores → Display ranking on web UI

## NOT Included in MVP (Future Additions)

- User authentication
- PostgreSQL database (MVP uses JSON files)
- Full checklist items (MVP implements 1-2 items per category)
- DCF calculation
- Automated data update jobs
- Polished UI (function over form)
- Cloud deployment

---

## Technology Stack

### Backend
- Python 3.11+
- FastAPI
- yfinance (free data source)
- PyYAML (configuration files)
- Data storage: Local JSON files

### Frontend
- TypeScript
- React 18 + Vite
- Tailwind CSS

### Development Environment
- VS Code + Claude Code extension

---

## Project Structure

```
buffett-mvp/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── watchlist_loader.py  # YAML watchlist loader
│   ├── data_collector.py    # yfinance data collection
│   ├── scorer.py            # Score calculation logic
│   ├── models.py            # Pydantic data models
│   ├── watchlist.yaml       # Watchlist configuration (user-editable)
│   ├── data/                # Cached financial data (JSON files)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── RankingList.tsx
│   │   │   ├── StockCard.tsx
│   │   │   └── ScoreDetail.tsx
│   │   ├── api.ts
│   │   ├── types.ts
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── .gitignore
└── README.md
```

---

## Watchlist Configuration (`watchlist.yaml`)

### File Specification

User-editable configuration file. Allows adding/removing stocks without code changes.

```yaml
# Buffett-Style Checklist Watchlist
# Edit this file to add or remove stocks
# After editing, reload via API: POST /api/watchlist/reload

version: "1.0"
last_updated: "2026-05-10"

stocks:
  - ticker: VEEV
    sector: Healthcare IT
    
  - ticker: INTU
    sector: Software
    
  - ticker: ADBE
    sector: Software
    
  - ticker: ADSK
    sector: Software
    
  - ticker: MSFT
    sector: Software
    
  - ticker: BRK.B
    sector: Conglomerate
```

### Validation Rules

- `ticker`: Required, alphanumeric with dots and hyphens only, 1-10 characters
- `sector`: Required, arbitrary string
- Duplicate tickers are forbidden (warning logged, entry skipped)
- Invalid entries are logged as errors and skipped

### Design for Future Extension

The following fields are reserved for future use. The MVP ignores them but accepts them in the structure:

```yaml
stocks:
  - ticker: VEEV
    sector: Healthcare IT
    # --- Fields below are unused in MVP, planned for Phase 2+ ---
    priority: high              # high | medium | low
    tags:                       # Arbitrary classification tags
      - vertical-saas
      - regulated
      - ai-resistant
    notes: |                    # Investment notes (multi-line allowed)
      Vertical SaaS specialized in life sciences.
      Gaining share from Salesforce Life Sciences Cloud via Vault CRM.
    added_date: "2026-01-15"   # Date added to watchlist
    target_price: 180.0        # Target buy price (for future DCF integration)
```

### Group Feature (Phase 2+)

```yaml
# Planned feature for future phases
groups:
  core_holdings:
    description: "Core positions (long-term holds)"
    members:
      - VEEV
      - MSFT
      
  watchlist:
    description: "Watching (buy on price decline)"
    members:
      - ADBE
      - ADSK
```

### MVP Watchlist Loader Implementation

```python
# watchlist_loader.py
import yaml
import logging
from pathlib import Path
from typing import List
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
    # Standalone execution: print loaded watchlist
    wl = load_watchlist()
    print(f"Loaded {len(wl.stocks)} stocks (version {wl.version}):")
    for stock in wl.stocks:
        print(f"  - {stock.ticker:8} ({stock.sector})")
```

---

## Buffett-Style Evaluation Categories

Total score (0-100) is calculated as a weighted average of 5 category scores.

| Category | Weight | MVP Implementation |
|----------|--------|--------------------|
| Business Understanding | 15% | Long-term revenue growth stability |
| Economic Moat | 25% | 10-year average ROE, operating margin stability |
| Management Quality | 15% | EPS growth vs share count change |
| Financial Health | 20% | Equity ratio, debt/EBITDA |
| Intrinsic Value & Margin of Safety | 25% | Current PER vs 10-year average PER |

### MVP Scoring Logic Details

#### Business Understanding (MVP Simplified)

```
Revenue CAGR (5-year):
- >= 10%: 100 points
- 5-10%: 70 points
- 0-5%: 40 points
- Negative: 0 points
```

#### Economic Moat

```
ROE 10-year average:
- >= 20%: 100 points
- 15-20%: 80 points
- 10-15%: 50 points
- < 10%: 20 points
```

#### Management Quality (MVP Simplified)

```
5-year EPS growth rate vs shares outstanding change:
- EPS growth > 0 AND shares decreasing: 100 points (ideal buybacks)
- EPS growth > 0 AND shares flat: 80 points
- EPS growth > shares increase rate: 50 points
- Otherwise: 30 points
```

#### Financial Health

```
Equity ratio (equity / total assets):
- >= 50%: 100 points
- 40-50%: 80 points
- 30-40%: 50 points
- < 30%: 20 points

Debt/EBITDA ratio:
- <= 1.0: 100 points
- 1.0-2.0: 80 points
- 2.0-3.0: 50 points
- > 3.0: 20 points

Final: average of both metrics
```

#### Intrinsic Value & Margin of Safety

```
Current PER vs 5-year average PER:
- Current <= 70% of average: 100 points (deeply undervalued)
- Current <= 85% of average: 70 points
- Current ~ average: 50 points
- Current > 115% of average: 20 points (overvalued)
```

#### Total Score

```
total_score = (
    business_score * 0.15 +
    moat_score * 0.25 +
    management_score * 0.15 +
    financial_score * 0.20 +
    value_score * 0.25
)
```

### Score Interpretation

- 75-100: "Buy candidate" (green)
- 55-75: "Watch" (yellow)
- 0-55: "Pass" (red)

---

## API Endpoints

### `GET /api/health`
```json
{ "status": "ok" }
```

### `GET /api/watchlist`
Get current watchlist
```json
{
  "version": "1.0",
  "last_updated": "2026-05-10",
  "stocks": [
    { "ticker": "VEEV", "sector": "Healthcare IT" }
  ]
}
```

### `POST /api/watchlist/reload`
Reload watchlist from YAML file
```json
{ "status": "reloaded", "stock_count": 6 }
```

### `GET /api/stocks`
Get all stocks with summary scores (for ranking display)
```json
[
  {
    "ticker": "VEEV",
    "name": "Veeva Systems",
    "sector": "Healthcare IT",
    "total_score": 78,
    "category_scores": {
      "business": 85,
      "moat": 90,
      "management": 75,
      "financial": 80,
      "value": 60
    },
    "judgment": "buy",
    "current_price": 220.50,
    "last_updated": "2026-05-10T12:00:00Z"
  }
]
```

### `GET /api/stocks/{ticker}`
Get detailed information for a specific stock (including financial data)

### `POST /api/stocks/{ticker}/refresh`
Refresh data and recalculate scores for a specific stock

### `POST /api/stocks/refresh-all`
Refresh data for all stocks in the watchlist

---

## Data Models (Pydantic)

### WatchlistEntry
```python
from pydantic import BaseModel, validator
from typing import Optional, List
import re

class WatchlistEntry(BaseModel):
    """A single entry in the watchlist (loaded from YAML)"""
    ticker: str
    sector: str
    # Reserved fields for future expansion (unused in MVP, but accepted)
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    added_date: Optional[str] = None
    target_price: Optional[float] = None
    
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
        # Allow unknown fields to pass through (for forward compatibility)
        extra = "allow"

class Watchlist(BaseModel):
    """Complete watchlist structure"""
    version: str = "1.0"
    last_updated: Optional[str] = None
    stocks: List[WatchlistEntry]
```

### Stock (Financial Evaluation Models)
```python
class Stock(BaseModel):
    ticker: str
    name: str
    sector: str
    current_price: float
    last_updated: datetime

class FinancialData(BaseModel):
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
    score: float  # 0-100
    details: dict
    
class StockEvaluation(BaseModel):
    stock: Stock
    financials: List[FinancialData]
    scores: dict[str, CategoryScore]
    total_score: float
    judgment: str  # "buy" | "watch" | "pass"
```

---

## Frontend UI Specification (MVP)

### Screen 1: Ranking Page (`/`)
- Display all stocks sorted by total score
- Each stock card shows:
  - Rank number
  - Ticker, company name, sector
  - Total score (prominent)
  - 5 category scores as mini bars
  - Judgment tag (buy/watch/pass)
- Click on card navigates to detail page
- Header has "Refresh All" button
- Display total stock count (from watchlist.yaml)

### Screen 2: Stock Detail Page (`/stocks/:ticker`)
- Top: Basic info (price, sector, last updated)
- Middle: Detailed scores per category with calculation breakdown
- Bottom: 10-year key financial metrics table
- "Refresh Data" button

### Style Guide
- Tailwind CSS
- Score color coding:
  - 75+: green (`text-green-600`)
  - 55-75: yellow (`text-yellow-600`)
  - <55: red (`text-red-600`)

---

## Development Steps

### Step 1: Environment Setup (30 minutes)

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install fastapi uvicorn yfinance pandas pydantic python-dotenv pyyaml
pip freeze > requirements.txt
```

#### Frontend
```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Step 2: Backend Implementation (4-6 hours)
1. Create `watchlist.yaml`
2. Define Pydantic models in `models.py`
3. Implement `watchlist_loader.py` (YAML loading)
4. Implement `data_collector.py` (yfinance integration)
5. Implement `scorer.py` (score calculation)
6. Implement `main.py` (FastAPI)
7. Verify at `http://localhost:8000/docs`

### Step 3: Frontend Implementation (4-6 hours)
1. Ranking page component
2. API client
3. Detail page
4. Verify at `http://localhost:5173`

### Step 4: Integration Testing (1-2 hours)

---

## Verification Checklist

- [ ] `python watchlist_loader.py` displays the watchlist
- [ ] `python data_collector.py VEEV` fetches VEEV financial data
- [ ] Backend starts: `uvicorn main:app --reload`
- [ ] Swagger UI accessible at `http://localhost:8000/docs`
- [ ] `GET /api/watchlist` returns YAML contents
- [ ] `GET /api/stocks` returns calculated scores
- [ ] Adding a new ticker to `watchlist.yaml` + `POST /api/watchlist/reload` updates the list
- [ ] Frontend starts: `npm run dev`
- [ ] Ranking displays at `http://localhost:5173`
- [ ] Stocks are sorted by score
- [ ] Clicking on a card navigates to the detail page
- [ ] Detail page shows financial data

---

## Future Phases

### Phase 2: Feature Expansion
- Display full YAML fields (notes, tags, priority) in UI
- Implement group feature
- Implement all checklist items
- Integrate SEC EDGAR API (higher data reliability)
- Migrate to PostgreSQL
- Automated data updates
- DCF calculation

### Phase 3: User Features
- Authentication
- Per-user watchlists
- Custom score weights
- Notes and evaluation records

### Phase 4: Cloud Deployment
- Backend: Railway / Render
- Frontend: Vercel
- Database: Supabase / Neon

---

## Initial Prompt for Claude Code

```
This project is the MVP of a Buffett-Style Checklist Ranking System.
Follow the specifications in buffett-mvp-spec.md.

First tasks (Step 1):

1. Create the project directory structure (backend/ and frontend/)
2. Create backend/watchlist.yaml with initial stocks:
   - VEEV (Healthcare IT)
   - INTU (Software)
   - ADBE (Software)
   - ADSK (Software)
   - MSFT (Software)
   - BRK.B (Conglomerate)
3. Create backend/models.py with Pydantic models (WatchlistEntry, Watchlist)
4. Create backend/watchlist_loader.py to load the YAML (with validation)
5. Create backend/data_collector.py to fetch data via yfinance
6. Create backend/main.py with a minimal FastAPI app:
   - GET /api/health
   - GET /api/watchlist
   - POST /api/watchlist/reload
7. Create requirements.txt

Verification:
- `python watchlist_loader.py` displays the stock list
- `python data_collector.py VEEV` displays VEEV financial data
- After `uvicorn main:app --reload`, `http://localhost:8000/api/watchlist`
  returns the YAML content

Stop here. Score calculation and frontend will be implemented in the next steps.

All code comments and docstrings must be in English.
```

## Second Prompt for Claude Code

```
Step 2: Implement scoring logic and add API endpoints.

Tasks:

1. Implement backend/scorer.py with the following functions:
   - calculate_business_score(financials) -> CategoryScore
     Based on 5-year revenue CAGR
   - calculate_moat_score(financials) -> CategoryScore
     Based on 10-year average ROE
   - calculate_management_score(financials) -> CategoryScore
     Based on 5-year EPS growth vs shares outstanding change
   - calculate_financial_score(financials) -> CategoryScore
     Based on equity ratio and debt/EBITDA
   - calculate_value_score(stock, financials) -> CategoryScore
     Based on current PER vs 5-year average PER
   - calculate_total_score(category_scores) -> float
     Weighted average: business 15%, moat 25%, management 15%, 
     financial 20%, value 25%
   - get_judgment(total_score) -> str
     Returns "buy" (>=75), "watch" (>=55), or "pass"
   
   Follow the exact scoring formulas in buffett-mvp-spec.md.
   Handle edge cases: missing data, division by zero, negative values, 
   insufficient historical data.
   Include English docstrings for all functions.
   Each CategoryScore.details should include the raw values used 
   (e.g., {"revenue_cagr_5y": 0.18, "data_points": 5}).

2. Create backend/services.py as a service layer that:
   - get_stock_evaluation(ticker) -> StockEvaluation
     Loads cached data from backend/data/{ticker}.json if available 
     and fresh (less than 24 hours old)
     Otherwise fetches fresh data via data_collector
     Combines data with calculated scores
     Saves results to backend/data/{ticker}.json
   - get_all_evaluations() -> List[StockEvaluation]
     Returns evaluations for all stocks in the watchlist
   - refresh_stock(ticker) -> StockEvaluation
     Forces a fresh data fetch and recalculation

3. Add the following API endpoints to backend/main.py:
   - GET /api/stocks
     Returns a list of all watchlist stocks with summary scores.
     Auto-fetches data for stocks without cache.
   - GET /api/stocks/{ticker}
     Returns detailed information including full financial history 
     and score breakdown.
     Returns 404 if ticker is not in the watchlist.
   - POST /api/stocks/{ticker}/refresh
     Forces refresh for a specific stock.
   - POST /api/stocks/refresh-all
     Refreshes all stocks. 
     Returns: { "status": "completed", "updated": N, "failed": M, "errors": [...] }

4. Ensure CORSMiddleware is configured in main.py to allow 
   requests from http://localhost:5173 with all methods and headers.

5. Add logging throughout (use Python's logging module) so we can 
   troubleshoot data issues.

Verification:
- curl http://localhost:8000/api/stocks returns scores for all 6 stocks
- curl http://localhost:8000/api/stocks/VEEV returns detailed VEEV data
- All scores are in 0-100 range
- judgment field is one of "buy", "watch", "pass"
- After POST /api/stocks/refresh-all, data files exist in backend/data/

Stop after backend is fully working. Frontend will be implemented next.
```

---

## Important Notes

- **This is NOT investment advice**: Scores are mechanical evaluations based on historical data. Investment decisions are the user's responsibility.
- **Data accuracy is not guaranteed**: yfinance is an unofficial API and may contain errors.
- **Designed for long-term holding**: Not for short-term trading decisions.

---

## References

- FastAPI: https://fastapi.tiangolo.com/
- yfinance: https://github.com/ranaroussi/yfinance
- React + Vite: https://vitejs.dev/guide/
- Tailwind CSS: https://tailwindcss.com/docs
- PyYAML: https://pyyaml.org/
