import React from 'react';
import './AboutPage.css';
import Logo from '../icons/logo.svg';
import Button from '../icons/button.svg';
import Play from '../icons/play_g.png';
import Next from '../icons/next_g.png';
import Previous from '../icons/previous_g.png';

export default function AboutPage() {
    const handleLogin = () => {
        // Przekieruj do backendu, który obsłuży autoryzację Spotify
        window.location.href = "http://localhost:8888/login";
    }

  return (
    <div className="about-page" role="main">
        <div className="navbar-container">
            <nav className="about-nav" role="navigation" aria-label="Nawigacja">
                <a href="/login" className="back-link" aria-label="Powrót do strony logowania">
                Powrót
                </a>
            </nav>
        </div>
      <div className="about-container">
        {/* Logo */}
        <div className="about-logo">
          <img 
            src={Logo}
            alt="Music. Logo" 
            className="logo-image"
          />
        </div>

        {/* Opis aplikacji */}
        <div className="about-description">
          <h1>O Aplikacji</h1>
          <p>
            <b>Music.</b> to eksperymentalna aplikacja webowa, której celem jest umożliwienie wygodniejszego sterowania muzyką na Spotify osobom z niepełnosprawnościami.
            <br></br>
            <br></br>
            Aplikacja została zaprojektowana zgodnie z wytycznymi WCAG 2.1 AA, co oznacza, że może być obsługiwana również przez osoby z ograniczoną sprawnością wzroku, słuchu czy motoryki.
            <br></br>
            <br></br>
            Podziękowania dla mojego promotora Krzysztofa Marka za pomoc w przygotowaniu tej aplikacji.
          </p>
        </div>

        <div className="about-description">
          <h2>Co możesz zrobić w aplikacji?</h2>
          <p>
          Aplikacja Music. jest oparta na Spotify przez co do poprawnego działania konieczne jest zalogowanie się do swojego konta Spotify. Music. posiada wszystkie podstawowe funkcje odtwarzacza muzycznego usprawnione o sterowanie za pomocą gestów oraz mowy.
          </p>
        </div>

        <div className="about-description">
          <h2>Dostępność</h2>
          <p>
          Aplikacja została przygotowana z myślą o dostępności:
          <ul>
            <li>Wysoki kontrast i czytelność tekstu</li>
            <li>Obsługa przycisków przez klawiaturę</li>
            <li>Wsparcie dla czytników ekranu (np. aria-label, role)</li>
            <li>Duże, wyraźne przyciski do obsługi</li>
          </ul>
          </p>
        </div>

        <div className="about-description">
          <h2>Wymagania techniczne</h2>
          <p>
          <ul>
            <li>Konto Spotify z aktywnym odtwarzaniem (np. przez aplikację mobilną lub desktopową)</li>
            <li>Dostęp do przeglądarki internetowej z mikrofonem (dla sterowania głosem)</li>
            <li><b>W przypadku gestów:</b> kamera z włączonym dostępem</li>
          </ul>
          </p>
        </div>

        <div className="about-description">
          <h2>Gesty</h2>
          <div className="about-gestures-container">
            <div className="about-gestures">
                <img src={Button} alt="Przycisk włączania gestów w aplikacji" />
            </div>
            <p>
                Funkcja gestów jest możliwa do włączenia w odtwarzaczu muzyki przyciskiem "Gesty".
            </p>
          </div>

          <div className="about-gestures-container">
            <h3>Gest "Play"</h3>
            <div className="about-gestures">
                <img src={Play} alt="Ilustracja gestu Play - sekwencja otwarta dłoń, zamknięta dłoń, otwarta dłoń" />
            </div>
            <p>
            Gest "Play" służy do wznowienia lub zatrzymania muzyki. Aby go wykonać należy przed kamerą wykonać następującą sekwencję:
            <ol>
              <li>Otwarta dłoń</li>
              <li>Zamknięta dłoń</li>       
              <li>Otwarta dłoń</li>     
            </ol>
            </p>
          </div>

          <div className="about-gestures-container">
            <h3>Gest "Next"</h3>
            <div className="about-gestures">
                <img src={Next} alt="Ilustracja gestu Next - sekwencja zamknięta dłoń, dłoń z palcem wskazującym, otwarta dłoń" />
            </div>
            <p>
            Gest "Next" służy do przewinięcia piosenki do kolejnej. Aby go wykonać należy przed kamerą wykonać następującą sekwencje:
            <ol>
              <li>Zamknięta dłoń</li>
              <li>Dłoń z wysuniętym palcem wskazującym</li>       
              <li>Otwarta dłoń</li>     
            </ol>
            </p>
          </div>

          <div className="about-gestures-container">
            <h3>Gest "Previous"</h3>
            <div className="about-gestures">
                <img src={Previous} alt="Ilustracja gestu Previous - sekwencja otwarta dłoń, dłoń z palcem wskazującym, zamknięta dłoń" />
            </div>
            <p>
            Gest "Previous" służy do przewinięcia piosenki do poprzedniej. Aby go wykonać należy przed kamerą wykonać następującą sekwencje:
            <ol>
              <li>Otwarta dłoń</li>
              <li>Dłoń z wysuniętym palcem wskazującym</li>       
              <li>Zamknięta dłoń</li>     
            </ol>
            </p>
          </div>
          
        </div>

      </div>
    </div>
  );
} 