# 🎯 System Rozpoznawania Gestów - Instrukcje

## 📋 Wymagania

### Backend (Python)
```bash
pip install -r backend/requirements.txt
```

### Frontend (Node.js)
```bash
cd frontend
npm install
```

## 🚀 Uruchamianie

### Opcja 1: Automatyczne uruchamianie (zalecane)
```bash
python start_servers.py
```

### Opcja 2: Ręczne uruchamianie

**Terminal 1 - Główny serwer API:**
```bash
cd backend
python main.py
```

**Terminal 2 - Serwer gestów:**
```bash
cd backend
python gesture_server.py
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm start
```

## 🎯 Obsługiwane gesty

### Sekwencja: open-close-open
- **Akcja:** Play/Pause
- **Opis:** Jeśli utwór gra - pauza, jeśli jest zatrzymany - wznowienie

## 🔧 Konfiguracja

### Porty
- **Frontend:** http://localhost:3000
- **API Server:** http://localhost:5000
- **Gesture Server:** http://localhost:5001

### Kamera
- System automatycznie używa domyślnej kamery (index 0)
- Wymagane uprawnienia do kamery w przeglądarce

## 🎮 Użycie

1. **Uruchom aplikację** zgodnie z instrukcjami powyżej
2. **Przejdź do Player** w aplikacji
3. **Kliknij "Włącz gesty"** w prawym górnym rogu
4. **Wykonaj sekwencję:** open-close-open
5. **Obserwuj** jak utwór przełącza się między play/pause

## 🐛 Rozwiązywanie problemów

### Problem: "Nie można otworzyć kamery"
- Sprawdź czy kamera nie jest używana przez inne aplikacje
- Sprawdź uprawnienia do kamery w systemie

### Problem: "Nie udało się połączyć z serwerem gestów"
- Sprawdź czy serwer gestów działa na porcie 5001
- Sprawdź logi w terminalu serwera gestów

### Problem: "Model nie został załadowany"
- Sprawdź czy plik `backend/gesture_recognition/src/model/model.h5` istnieje
- Sprawdź czy wszystkie zależności są zainstalowane

## 📁 Struktura plików

```
SpotifyWCAG/
├── backend/
│   ├── gesture_server.py      # Serwer gestów
│   ├── api.py                 # API Spotify
│   └── gesture_recognition/   # Model ML
├── frontend/
│   └── src/
│       └── components/
│           └── GestureHandler.jsx  # Komponent gestów
└── start_servers.py           # Skrypt uruchamiania
```

## 🔍 Debugowanie

### Logi serwera gestów
- Wykryte gesty: `🎯 Wykryto gest: open (pewność: 0.95)`
- Sekwencje: `🎵 Wykryto sekwencję: open-close-open`
- Akcje Spotify: `⏯️ Wykryto sekwencję open-close-open - przełączam play/pause`

### Logi frontendu
- Połączenie WebSocket: `🔌 Połączono z serwerem gestów`
- Wykryte gesty: `🎯 Gest: open (pewność: 0.95)`
- Akcje Spotify: `🎵 Akcja Spotify: play_pause - Przełączono play/pause` 