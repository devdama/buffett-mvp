import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { StockEvaluation, FinancialData, CategoryScore } from '../types';
import { fetchStock, refreshStock } from '../api';

function getScoreColor(score: number): string {
  if (score >= 75) return 'text-green-600';
  if (score >= 55) return 'text-yellow-600';
  return 'text-red-600';
}

function formatCurrency(value: number): string {
  if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
  if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
  if (value >= 1e3) return `$${(value / 1e3).toFixed(2)}K`;
  return `$${value.toFixed(2)}`;
}

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(2)}%`;
}

export default function ScoreDetail() {
  const { ticker } = useParams<{ ticker: string }>();
  const [evaluation, setEvaluation] = useState<StockEvaluation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadStock = async () => {
    if (!ticker) return;
    try {
      setLoading(true);
      setError(null);
      const data = await fetchStock(ticker);
      setEvaluation(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load stock');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStock();
  }, [ticker]);

  const handleRefresh = async () => {
    if (!ticker) return;
    try {
      setRefreshing(true);
      const data = await refreshStock(ticker);
      setEvaluation(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refresh');
    } finally {
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">Loading...</p>
      </div>
    );
  }

  if (!evaluation) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-red-600">{error || 'Stock not found'}</p>
      </div>
    );
  }

  const { stock, scores, financials, total_score } = evaluation;
  const categoryOrder = ['business', 'moat', 'management', 'financial', 'value'];
  const categoryLabels: Record<string, string> = {
    business: 'Business Understanding',
    moat: 'Economic Moat',
    management: 'Management Quality',
    financial: 'Financial Health',
    value: 'Intrinsic Value & Margin of Safety',
  };

  const lastYear = financials[financials.length - 1];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <Link to="/" className="text-blue-600 hover:text-blue-700">
            ← Back to Ranking
          </Link>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {refreshing ? 'Refreshing...' : 'Refresh Data'}
          </button>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Header */}
        <div className="bg-white rounded-lg p-6 mb-6 border border-gray-200">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{stock.ticker}</h1>
              <p className="text-xl text-gray-600">{stock.name}</p>
            </div>
            <div className="text-right">
              <p className={`text-3xl font-bold ${getScoreColor(total_score)}`}>
                {total_score}
              </p>
              <p className="text-sm text-gray-600">Total Score</p>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <p className="text-gray-600">Sector</p>
              <p className="font-semibold">{stock.sector}</p>
            </div>
            <div>
              <p className="text-gray-600">Current Price</p>
              <p className="font-semibold">${stock.current_price.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-gray-600">Last Updated</p>
              <p className="font-semibold">
                {new Date(stock.last_updated).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>

        {/* Category Scores */}
        <div className="space-y-4 mb-6">
          {categoryOrder.map((category) => {
            const scoreObj = scores[category] as CategoryScore;
            return (
              <div key={category} className="bg-white rounded-lg p-6 border border-gray-200">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-bold text-gray-900">
                    {categoryLabels[category]}
                  </h2>
                  <span className={`text-2xl font-bold ${getScoreColor(scoreObj.score)}`}>
                    {scoreObj.score}
                  </span>
                </div>
                <div className="mb-4 bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${getScoreColor(scoreObj.score)} transition-all`}
                    style={{ width: `${scoreObj.score}%` }}
                  />
                </div>
                <div className="text-sm text-gray-600 space-y-1">
                  {Object.entries(scoreObj.details).map(([key, value]) => {
                    let displayValue: string;
                    if (typeof value === 'number') {
                      if (key.includes('ratio') || key.includes('_pct') || key.includes('roe')) {
                        displayValue = formatPercent(value);
                      } else if (key.includes('revenue') || key.includes('income') || key.includes('equity') || key.includes('assets') || key.includes('debt') || key.includes('cf') || key.includes('ebitda')) {
                        displayValue = formatCurrency(value);
                      } else {
                        displayValue = value.toFixed(4);
                      }
                    } else {
                      displayValue = String(value);
                    }
                    return (
                      <div key={key} className="flex justify-between">
                        <span className="font-medium">{key}:</span>
                        <span>{displayValue}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>

        {/* Financial Table */}
        <div className="bg-white rounded-lg p-6 border border-gray-200">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Financial History</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Year</th>
                  <th className="text-right py-2 px-2 font-semibold text-gray-700">Revenue</th>
                  <th className="text-right py-2 px-2 font-semibold text-gray-700">Op. Income</th>
                  <th className="text-right py-2 px-2 font-semibold text-gray-700">Net Income</th>
                  <th className="text-right py-2 px-2 font-semibold text-gray-700">EPS</th>
                  <th className="text-right py-2 px-2 font-semibold text-gray-700">Equity Ratio</th>
                  <th className="text-right py-2 px-2 font-semibold text-gray-700">Debt/EBITDA</th>
                </tr>
              </thead>
              <tbody>
                {financials.map((f: FinancialData, idx) => {
                  const equityRatio = f.total_assets > 0 ? f.total_equity / f.total_assets : 0;
                  const debtEbitda =
                    f.operating_income > 0 ? f.total_debt / f.operating_income : 0;
                  return (
                    <tr key={idx} className="border-b border-gray-100">
                      <td className="py-2 px-2">{f.fiscal_year}</td>
                      <td className="text-right py-2 px-2">{formatCurrency(f.revenue)}</td>
                      <td className="text-right py-2 px-2">
                        {formatCurrency(f.operating_income)}
                      </td>
                      <td className="text-right py-2 px-2">{formatCurrency(f.net_income)}</td>
                      <td className="text-right py-2 px-2">${f.eps.toFixed(2)}</td>
                      <td className="text-right py-2 px-2">{formatPercent(equityRatio)}</td>
                      <td className="text-right py-2 px-2">{debtEbitda.toFixed(2)}x</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
