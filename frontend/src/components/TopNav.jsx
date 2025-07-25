import React from 'react';
import './TopNav.css';

export default function TopNav({ currentView = 'home', onViewChange = () => {} }) {
  const views = [
    { id: 'home', label: 'Home' },
    { id: 'recently-played', label: 'Recently Played' },
    { id: 'albums', label: 'Albums' },
    { id: 'playlists', label: 'Playlists' }
  ];

  return (
    <nav className="topnav-root" role="navigation" aria-label="Główne menu nawigacyjne">
      {views.map(view => (
        <button
          key={view.id}
          className={`topnav-btn ${currentView === view.id ? 'topnav-btn-active' : ''}`}
          onClick={() => onViewChange(view.id)}
          aria-current={currentView === view.id ? 'page' : undefined}
          aria-label={`Przejdź do sekcji ${view.label}`}
        >
          {view.label}
        </button>
      ))}
    </nav>
  );
} 