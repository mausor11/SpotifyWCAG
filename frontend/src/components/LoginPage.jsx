import React from 'react';
import './LoginPage.css';
import Logo from '../icons/logo.svg';

export default function LoginPage() {
    const handleLogin = () => {
        // Przekieruj do backendu, który obsłuży autoryzację Spotify
        window.location.href = "http://localhost:8888/login";
    }

  return (
    <div className="login-page" role="main">
      <div className="login-container">
        {/* Logo */}
        <div className="login-logo">
          <img 
            src={Logo}
            alt="Music. Logo" 
            className="logo-image"
          />
        </div>

        {/* Opis aplikacji */}
        <div className="login-description">
          <h1 className="sr-only">Logowanie do Music.</h1>
          <p>
            Music. to aplikacja dostosowująca Spotify dla osób niepełnosprawnych. 
            Została usprawniona o sterowanie muzyką gestami oraz mową.
          </p>
        </div>

        {/* Call to action */}
        <div className="login-cta">
          <p>Zaloguj się, aby kontynuować</p>
        </div>

        {/* Przycisk logowania */}
        <button 
          className="login-button"
          onClick={handleLogin}
          aria-label="Zaloguj się do Spotify"
        >
          Zaloguj się
        </button>

        {/* Footer z linkiem */}
        <div className="login-footer">
          <a href="/about" className="learn-more-link" aria-label="Dowiedz się więcej o aplikacji Music.">
            Dowiedz się więcej o aplikacji Music.
          </a>
        </div>
      </div>
    </div>
  );
} 