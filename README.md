# Buffett MVP: Stock Ranking System

A Buffett-style investment checklist ranking system that evaluates stocks across 5 key categories: Business Quality, Moat, Management, Financial Health, and Valuation.

## Project Structure

```
buffett-mvp/
├── backend/           # FastAPI scoring engine
│   ├── main.py        # API endpoints
│   ├── scorer.py      # 5-category evaluation logic
│   ├── services.py    # Data orchestration
│   ├── data_collector.py
│   ├── watchlist_loader.py
│   ├── watchlist.yaml # Stock watchlist
│   ├── requirements.txt
│   └── data/          # Cached financial data (JSON)
└── frontend/          # React + TypeScript + Vite
    ├── src/
    │   ├── components/
    │   │   ├── RankingList.tsx
    │   │   ├── StockCard.tsx
    │   │   └── ScoreDetail.tsx
    │   ├── App.tsx
    │   ├── types.ts
    │   ├── api.ts
    │   └── index.css
    └── package.json
```

## Prerequisites

- **Python**: 3.11+ (recommended 3.14+)
- **Node.js**: 18+ (via nvm recommended)
- **Git**: for version control

## Quick Start

### 1. Install Python Environment

```bash
# Check Python version
python3 --version  # Should be 3.11+

# If using nvm for Node (optional):
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash
source ~/.nvm/nvm.sh
nvm install --lts
nvm use --lts
```

### 2. Backend Setup

```bash
cd backend

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install

# Verify installation
npm --version
```

## Running the Project

### Terminal 1: Start Backend

```bash
cd backend

# Activate venv (if not already active)
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate    # Windows

# Start FastAPI server
uvicorn main:app --reload
```

Server runs on: **http://localhost:8000**

Available endpoints:
- `GET /api/health` — health check
- `GET /api/watchlist` — list of stocks
- `POST /api/watchlist/reload` — reload from YAML
- `GET /api/stocks` — ranked evaluations (sorted by score)
- `GET /api/stocks/{ticker}` — single stock evaluation
- `POST /api/stocks/{ticker}/refresh` — force refresh stock data
- `POST /api/stocks/refresh-all` — force refresh all stocks

### Terminal 2: Start Frontend

```bash
cd frontend

# Start Vite dev server
npm run dev
```

Frontend runs on: **http://localhost:5173**

Open your browser and navigate to `http://localhost:5173` to see the ranking list.

## Verification Checklist

After both servers are running:

1. **Backend Health**
   ```bash
   curl http://localhost:8000/api/health
   # Expected: {"status": "ok"}
   ```

2. **Fetch All Stocks**
   ```bash
   curl http://localhost:8000/api/stocks | python3 -m json.tool
   # Expected: list of 6 stocks with scores, sorted descending
   ```

3. **Frontend Access**
   - Open http://localhost:5173 in browser
   - Should see "Buffett Ranking" header with 6 stock cards
   - Each card shows: rank, ticker, name, sector, total score, judgment (BUY/WATCH/PASS), and 5 category scores with filled bars

4. **Navigation Test**
   - Click a stock card → should navigate to detail page
   - Should display full financial data and score breakdown

5. **Refresh Button**
   - Click "Refresh All" button → updates all stock data
   - Should show loading state and refresh timestamp

## Scoring System

### 5 Categories (weighted)

| Category | Weight | Formula |
|----------|--------|---------|
| Business | 15% | Revenue CAGR over 5 years |
| Moat | 25% | Average ROE (Return on Equity) |
| Management | 15% | EPS growth vs. share buybacks |
| Financial | 20% | Equity ratio + Debt/EBITDA |
| Value | 25% | Current P/E vs. 5-year average P/E |

### Score Ranges

- **Buy** ≥ 75
- **Watch** 55–74
- **Pass** < 55

### Score Color Coding

- 🟢 Green: ≥ 75 (strong)
- 🟡 Yellow: 55–74 (moderate)
- 🔴 Red: < 55 (weak)

## Data Flow

1. **Data Collection**: yfinance downloads stock financials
2. **Caching**: JSON cache in `backend/data/` (24-hour TTL)
3. **Scoring**: 5 scorers evaluate cached data
4. **API**: FastAPI serves evaluations
5. **Frontend**: React fetches and displays rankings

## Common Commands

```bash
# Backend: Reload from watchlist YAML
curl -X POST http://localhost:8000/api/watchlist/reload

# Backend: Refresh single stock
curl -X POST http://localhost:8000/api/stocks/MSFT/refresh

# Backend: Refresh all stocks
curl -X POST http://localhost:8000/api/stocks/refresh-all

# Frontend: Build for production
cd frontend && npm run build

# Frontend: Preview production build
cd frontend && npm run preview
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'fastapi'"
- Ensure virtual environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### "Port 8000 already in use"
- Use different port: `uvicorn main:app --reload --port 8001`

### "Cannot GET /api/stocks" (CORS/proxy error)
- Ensure backend is running on port 8000
- Check vite.config.ts has proxy configured: `/api` → `http://localhost:8000`
- Clear browser cache and refresh

### Score bars not filling proportionally
- Hard refresh browser: `Cmd+Shift+R` (macOS) or `Ctrl+Shift+R` (Windows/Linux)
- Check browser console for errors (F12)

### "Invalid response from backend"
- Verify yfinance can reach Yahoo Finance (may fail if internet is slow)
- Check data exists: `ls backend/data/`
- Manually fetch data: `python3 backend/data_collector.py MSFT`

## Development

### Backend: Add new stock to watchlist
Edit `backend/watchlist.yaml`:
```yaml
stocks:
  - ticker: NEWSTOCK
    name: New Stock Company
    sector: Technology
```

Then reload: `curl -X POST http://localhost:8000/api/watchlist/reload`

### Frontend: Modify styling
- Edit `frontend/src/index.css` for global styles
- Edit `frontend/src/components/*.tsx` for component styles
- Uses Tailwind CSS utility classes

## Project Status

✅ Step 1: Data pipeline (yfinance → JSON cache)  
✅ Step 2: Scoring engine (5 categories with API endpoints)  
✅ Step 3: Frontend (ranking list + detail page)  

## License

MIT
