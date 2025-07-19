import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useState } from 'react';
import HomePage from './components/HomePage';
import Player from './components/Player';
import RecentlyPlayed from './components/RecentlyPlayed';
import Albums from './components/Albums';
import Playlists from './components/Playlists';
import './App.css';

export default function App() {
  const [currentView, setCurrentView] = useState('home');

  const handleViewChange = (view) => {
    setCurrentView(view);
  };

  const renderMainContent = () => {
    switch (currentView) {
      case 'home':
        return <HomePage currentView={currentView} onViewChange={handleViewChange} />;
      case 'recently-played':
        return <RecentlyPlayed currentView={currentView} onViewChange={handleViewChange} />;
      case 'albums':
        return <Albums currentView={currentView} onViewChange={handleViewChange} />;
      case 'playlists':
        return <Playlists currentView={currentView} onViewChange={handleViewChange} />;
      default:
        return <HomePage currentView={currentView} onViewChange={handleViewChange} />;
    }
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={renderMainContent()} />
        <Route path="/player" element={<Player />} />
      </Routes>
    </BrowserRouter>
  );
}
