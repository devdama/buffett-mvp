import { Link } from 'react-router-dom';
import { StockEvaluation, CategoryScore } from '../types';

interface Props {
  evaluation: StockEvaluation;
  rank: number;
}

function getScoreColor(score: number): string {
  if (score >= 75) return 'text-green-600';
  if (score >= 55) return 'text-yellow-600';
  return 'text-red-600';
}

function getJudgmentBgColor(judgment: string): string {
  if (judgment === 'buy') return 'bg-green-100 text-green-800';
  if (judgment === 'watch') return 'bg-yellow-100 text-yellow-800';
  return 'bg-red-100 text-red-800';
}

function ScoreBar({ label, score }: { label: string; score: number }) {
  const color = getScoreColor(score);
  const bgColor = color === 'text-green-600' ? '#10b981' : color === 'text-yellow-600' ? '#ca8a04' : '#dc2626';

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '14px', marginBottom: '8px' }}>
      <span style={{ width: '80px', color: '#374151', fontWeight: '500' }}>{label}</span>
      <div style={{ flex: 1, backgroundColor: '#d1d5db', borderRadius: '6px', height: '16px', overflow: 'hidden' }}>
        <div
          style={{
            height: '16px',
            backgroundColor: bgColor,
            width: `${score}%`,
            borderRadius: '6px',
            transition: 'width 0.3s ease',
          }}
        />
      </div>
      <span style={{ width: '40px', textAlign: 'right', fontWeight: 'bold', color: bgColor }}>{Math.round(score)}</span>
    </div>
  );
}

export default function StockCard({ evaluation, rank }: Props) {
  const { stock, scores, total_score, judgment } = evaluation;
  const categoryOrder = ['business', 'moat', 'management', 'financial', 'value'];
  const categoryLabels: Record<string, string> = {
    business: 'Business',
    moat: 'Moat',
    management: 'Mgmt',
    financial: 'Finance',
    value: 'Value',
  };

  return (
    <Link
      to={`/stocks/${stock.ticker}`}
      className="block p-6 bg-white rounded-lg border border-gray-200 hover:shadow-lg transition-shadow cursor-pointer"
    >
      <div className="mb-4">
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center gap-4">
            <div className="flex items-center justify-center w-10 h-10 bg-gray-200 rounded-full font-bold text-gray-700">
              #{rank}
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">{stock.ticker}</h3>
              <p className="text-sm text-gray-600">{stock.name}</p>
            </div>
          </div>
          <span
            className={`px-3 py-1 rounded-full text-sm font-semibold ${getJudgmentBgColor(
              judgment
            )}`}
          >
            {judgment.toUpperCase()}
          </span>
        </div>
        <p className="text-sm text-gray-500">{stock.sector}</p>
      </div>

      <div className="mb-4 p-3 bg-blue-50 rounded-lg">
        <span className="text-sm text-gray-600">Total Score: </span>
        <span className={`text-2xl font-bold ${getScoreColor(total_score)}`}>
          {total_score}
        </span>
      </div>

      <div className="space-y-2">
        {categoryOrder.map((category) => {
          const scoreObj = scores[category] as CategoryScore;
          return (
            <ScoreBar
              key={category}
              label={categoryLabels[category]}
              score={scoreObj?.score ?? 0}
            />
          );
        })}
      </div>
    </Link>
  );
}
