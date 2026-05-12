# Frontend: Buffett MVP Ranking System

React + TypeScript + Vite frontend for the Buffett stock ranking system.

## Quick Start

### Prerequisites
- **Node.js**: 18+ (check with `node --version`)
- **Backend running**: http://localhost:8000 (see root README for setup)

### Installation

```bash
cd frontend

# Install dependencies
npm install
```

### Development Server

```bash
# Start Vite dev server (with hot reload)
npm run dev
```

Frontend runs on: **http://localhost:5173**

The dev server automatically proxies API calls to `http://localhost:8000` (see `vite.config.ts`).

### Production Build

```bash
# Build optimized bundle
npm run build

# Preview production build locally
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── RankingList.tsx    # Main listing page (/)
│   │   ├── StockCard.tsx      # Stock card component
│   │   └── ScoreDetail.tsx    # Detail page (/stocks/:ticker)
│   ├── App.tsx                # Router setup
│   ├── types.ts               # TypeScript type definitions
│   ├── api.ts                 # API fetch wrapper functions
│   ├── main.tsx               # Entry point
│   └── index.css              # Global styles (Tailwind)
├── vite.config.ts             # Vite configuration + API proxy
├── tailwind.config.js         # Tailwind CSS setup
├── tsconfig.app.json          # TypeScript config
├── package.json               # Dependencies
└── index.html                 # HTML entry point
```

## Key Features

### Pages

1. **Ranking List** (`/`)
   - Displays all stocks sorted by total score (highest first)
   - Shows: rank, ticker, name, sector, judgment, total score, 5 category bars
   - "Refresh All" button to fetch latest data
   - Click card to view details

2. **Stock Detail** (`/stocks/:ticker`)
   - Full company information
   - Detailed score breakdown with metrics
   - Financial data table (revenue, net income, ROE, debt ratios, etc.)
   - "Refresh Data" button to force update
   - "Back" link to ranking list

### Scoring Visualization

- **Score colors**: Green (≥75), Yellow (55–74), Red (<55)
- **Category bars**: Fill proportionally to score (0–100%)
- **Judgment tags**: BUY / WATCH / PASS with color coding

## Available Scripts

```bash
# Start dev server (with HMR)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type-check without build
npx tsc --noEmit
```

## API Integration

All API calls proxied through `http://localhost:8000` via `vite.config.ts`.

### Endpoints Used

```typescript
GET  /api/stocks              // Fetch all evaluations
GET  /api/stocks/{ticker}     // Fetch single stock
POST /api/stocks/refresh-all  // Refresh all stocks
POST /api/stocks/{ticker}/refresh  // Refresh single stock
```

See [src/api.ts](src/api.ts) for implementation.

## Troubleshooting

### "Cannot GET /api/stocks"
1. Verify backend running: `curl http://localhost:8000/api/health`
2. Check vite.config.ts proxy: `/api` → `http://localhost:8000`
3. Hard refresh browser: `Cmd+Shift+R` (macOS) or `Ctrl+Shift+R` (Windows/Linux)

### Score bars not filling correctly
- Hard refresh browser cache (Cmd+Shift+R)
- Open DevTools (F12) and check console for errors
- Verify API returns valid score values (0–100)

### TypeScript errors
- Run type-check: `npx tsc --noEmit`
- Ensure all imports use correct type syntax: `import type { Type } from './file'`

### Module not found errors
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`
- Clear npm cache: `npm cache clean --force`

## Dependencies

| Package | Purpose |
|---------|---------|
| react | UI framework |
| react-router-dom | Routing (v6) |
| tailwindcss | Utility CSS framework |
| vite | Build tool & dev server |
| typescript | Type safety |

See `package.json` for exact versions.

## Technologies

- **Build**: Vite 5+ (fast dev server, optimized bundles)
- **UI Framework**: React 18+ with TypeScript
- **Styling**: Tailwind CSS 3+ (utility-first)
- **Routing**: React Router v6
- **Data Fetching**: Native Fetch API (no external HTTP library)

## Full Setup Instructions

For complete backend + frontend setup, see the root [README.md](../README.md).
