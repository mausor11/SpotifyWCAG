import React from 'react';
import './TopNav.css';

export default function TopNav() {
  return (
    <nav className="topnav-root">
      <button className="topnav-btn topnav-btn-active">Home</button>
      <button className="topnav-btn">Recently Played</button>
      <button className="topnav-btn">Albums</button>
      <button className="topnav-btn">Playlists</button>
    </nav>
  );
} 