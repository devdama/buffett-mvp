import { useState, useEffect } from 'react';
import { StockEvaluation } from '../types';
import { fetchStocks, refreshAllStocks } from '../api';
import StockCard from './StockCard';

export default function RankingList() {
  const [stocks, setStocks] = useState<StockEvaluation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadStocks = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchStocks();
      setStocks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load stocks');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStocks();
  }, []);

  const handleRefreshAll = async () => {
    try {
      setRefreshing(true);
      await refreshAllStocks();
      await loadStocks();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refresh');
    } finally {
      setRefreshing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-900">Buffett Ranking</h1>
            <p className="text-gray-600 mt-2">{stocks.length} stocks evaluated</p>
          </div>
          <button
            onClick={handleRefreshAll}
            disabled={refreshing}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {refreshing ? 'Refreshing...' : 'Refresh All'}
          </button>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-600">Loading...</p>
          </div>
        ) : (
          <div className="space-y-4">
            {stocks.map((evaluation, idx) => (
              <StockCard
                key={evaluation.stock.ticker}
                evaluation={evaluation}
                rank={idx + 1}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
