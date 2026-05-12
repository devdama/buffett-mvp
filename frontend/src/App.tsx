import { BrowserRouter, Routes, Route } from 'react-router-dom';
import RankingList from './components/RankingList';
import ScoreDetail from './components/ScoreDetail';
import './index.css';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<RankingList />} />
        <Route path="/stocks/:ticker" element={<ScoreDetail />} />
      </Routes>
    </BrowserRouter>
  );
}
