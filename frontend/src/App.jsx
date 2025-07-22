import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import axios from 'axios';
import HomePage from './components/HomePage';
import Player from './components/Player';
import RecentlyPlayed from './components/RecentlyPlayed';
import Albums from './components/Albums';
import Playlists from './components/Playlists';
import LoginPage from './components/LoginPage';
import AboutPage from './components/AboutPage';
import './App.css';

// Komponent do sprawdzania autoryzacji
function ProtectedRoute({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const location = useLocation();

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/auth-status');
      setIsAuthenticated(response.data.authenticated);
    } catch (error) {
      console.error('❌ Błąd sprawdzania statusu autoryzacji:', error);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  };

  // Pokaż loading podczas sprawdzania
  if (isLoading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        backgroundColor: '#000000',
        color: 'white'
      }}>
        <div>Ładowanie...</div>
      </div>
    );
  }

  // Jeśli nie jest zalogowany, przekieruj do /login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Jeśli jest zalogowany, pokaż chronioną zawartość
  return children;
}

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
        {/* Strona logowania - dostępna bez autoryzacji */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/about" element={<AboutPage />} />
        {/* Chronione trasy - wymagają autoryzacji */}
        <Route path="/" element={
          <ProtectedRoute>
            {renderMainContent()}
          </ProtectedRoute>
        } />
        <Route path="/player" element={
          <ProtectedRoute>
            <Player />
          </ProtectedRoute>
        } />
      </Routes>
    </BrowserRouter>
  );
}
