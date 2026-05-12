import sys
import json
import logging
from pathlib import Path
from datetime import datetime
import yfinance as yf
import pandas as pd

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def fetch_stock_data(ticker: str) -> dict:
    """
    Fetch financial data for a ticker via yfinance.
    Returns a dict with current price, company info, and annual financials.
    """
    yf_ticker = yf.Ticker(ticker)
    info = yf_ticker.info

    current_price = info.get("currentPrice") or info.get("regularMarketPrice", 0.0)
    trailing_pe = info.get("trailingPE")
    name = info.get("longName") or info.get("shortName", ticker)
    sector = info.get("sector", "Unknown")

    income_stmt = yf_ticker.financials  # annual, columns = fiscal year end dates
    balance_sheet = yf_ticker.balance_sheet
    cash_flow = yf_ticker.cashflow

    financials = []
    if income_stmt is not None and not income_stmt.empty:
        for col in income_stmt.columns:
            year = int(col.year if hasattr(col, 'year') else int(str(col)[:4]))

            def get_val(df, *keys):
                for key in keys:
                    if df is not None and key in df.index and col in df.columns:
                        val = df.loc[key, col]
                        if pd.notna(val):
                            return float(val)
                return 0.0

            revenue = get_val(income_stmt, "Total Revenue")
            operating_income = get_val(income_stmt, "Operating Income")
            net_income = get_val(income_stmt, "Net Income")
            eps = get_val(income_stmt, "Diluted EPS", "Basic EPS")

            shares = get_val(balance_sheet, "Ordinary Shares Number", "Share Issued")
            if shares == 0.0:
                shares = info.get("sharesOutstanding", 0.0)

            total_assets = get_val(balance_sheet, "Total Assets")
            total_equity = get_val(
                balance_sheet,
                "Stockholders Equity",
                "Total Equity Gross Minority Interest",
            )
            total_debt = get_val(balance_sheet, "Total Debt", "Long Term Debt")
            operating_cf = get_val(cash_flow, "Operating Cash Flow")
            capex = get_val(cash_flow, "Capital Expenditure")
            free_cf = operating_cf + capex  # capex is already negative in yfinance

            financials.append({
                "fiscal_year": year,
                "revenue": revenue,
                "operating_income": operating_income,
                "net_income": net_income,
                "eps": eps,
                "shares_outstanding": shares,
                "total_assets": total_assets,
                "total_equity": total_equity,
                "total_debt": total_debt,
                "operating_cash_flow": operating_cf,
                "free_cash_flow": free_cf,
            })

    financials.sort(key=lambda x: x["fiscal_year"])

    result = {
        "ticker": ticker.upper(),
        "name": name,
        "sector": sector,
        "current_price": current_price,
        "trailing_pe": trailing_pe,
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "financials": financials,
    }
    return result


def save_stock_data(ticker: str, data: dict) -> Path:
    """Save fetched data as a JSON file in the data/ directory."""
    path = DATA_DIR / f"{ticker.upper()}.json"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path


def load_stock_data(ticker: str) -> dict | None:
    """Load cached stock data from the data/ directory."""
    path = DATA_DIR / f"{ticker.upper()}.json"
    if not path.exists():
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ticker = sys.argv[1] if len(sys.argv) > 1 else "VEEV"
    print(f"Fetching data for {ticker} ...")
    data = fetch_stock_data(ticker)
    path = save_stock_data(ticker, data)
    print(f"Saved to {path}")
    print(f"\nCompany : {data['name']}")
    print(f"Sector  : {data['sector']}")
    print(f"Price   : ${data['current_price']:.2f}")
    print(f"\nAnnual financials ({len(data['financials'])} years):")
    for f in data['financials']:
        rev_b = f['revenue'] / 1e9
        ni_b = f['net_income'] / 1e9
        print(
            f"  {f['fiscal_year']}: Revenue ${rev_b:.2f}B  "
            f"Net Income ${ni_b:.2f}B  EPS ${f['eps']:.2f}"
        )
