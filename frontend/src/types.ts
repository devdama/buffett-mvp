export type FinancialData = {
  fiscal_year: number;
  revenue: number;
  operating_income: number;
  net_income: number;
  eps: number;
  shares_outstanding: number;
  total_assets: number;
  total_equity: number;
  total_debt: number;
  operating_cash_flow: number;
  free_cash_flow: number;
};

export type CategoryScore = {
  score: number;
  details: Record<string, unknown>;
};

export type Stock = {
  ticker: string;
  name: string;
  sector: string;
  current_price: number;
  last_updated: string;
};

export type StockEvaluation = {
  stock: Stock;
  financials: FinancialData[];
  scores: Record<string, CategoryScore>;
  total_score: number;
  judgment: 'buy' | 'watch' | 'pass';
};
