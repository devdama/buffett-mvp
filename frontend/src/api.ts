import { StockEvaluation } from './types';

const BASE = '/api';

export async function fetchStocks(): Promise<StockEvaluation[]> {
  const res = await fetch(`${BASE}/stocks`);
  if (!res.ok) throw new Error(`Failed to fetch stocks: ${res.statusText}`);
  return res.json();
}

export async function fetchStock(ticker: string): Promise<StockEvaluation> {
  const res = await fetch(`${BASE}/stocks/${ticker}`);
  if (!res.ok) throw new Error(`Failed to fetch ${ticker}: ${res.statusText}`);
  return res.json();
}

export async function refreshAllStocks(): Promise<{
  status: string;
  updated: number;
  failed: number;
  errors: unknown[];
}> {
  const res = await fetch(`${BASE}/stocks/refresh-all`, { method: 'POST' });
  if (!res.ok) throw new Error(`Failed to refresh all: ${res.statusText}`);
  return res.json();
}

export async function refreshStock(ticker: string): Promise<StockEvaluation> {
  const res = await fetch(`${BASE}/stocks/${ticker}/refresh`, { method: 'POST' });
  if (!res.ok) throw new Error(`Failed to refresh ${ticker}: ${res.statusText}`);
  return res.json();
}
