#!/usr/bin/env python3
"""
Test systemu rozpoznawania gestów
"""

import requests
import time
import json

def test_gesture_server():
    """Testuje serwer gestów"""
    print("🧪 Testowanie serwera gestów...")
    
    # Test 1: Sprawdź czy serwer odpowiada
    try:
        response = requests.get('http://127.0.0.1:5001/gestures/status', timeout=5)
        if response.status_code == 200:
            print("✅ Serwer gestów odpowiada")
            data = response.json()
            print(f"   Status: {data.get('active', 'unknown')}")
            print(f"   Historia: {data.get('history', [])}")
        else:
            print(f"❌ Serwer gestów nie odpowiada poprawnie: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Nie można połączyć się z serwerem gestów")
        print("   Upewnij się, że serwer jest uruchomiony: python backend/gesture_server.py")
        return False
    except Exception as e:
        print(f"❌ Błąd testowania serwera gestów: {e}")
        return False
    
    # Test 2: Włącz rozpoznawanie gestów
    try:
        response = requests.post('http://127.0.0.1:5001/gestures/toggle', 
                               json={'enable': True}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Rozpoznawanie gestów: {data.get('status')}")
        else:
            print(f"❌ Błąd włączania gestów: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Błąd włączania gestów: {e}")
        return False
    
    # Test 3: Wyłącz rozpoznawanie gestów
    try:
        response = requests.post('http://127.0.0.1:5001/gestures/toggle', 
                               json={'enable': False}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Rozpoznawanie gestów: {data.get('status')}")
        else:
            print(f"❌ Błąd wyłączania gestów: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Błąd wyłączania gestów: {e}")
        return False
    
    return True

def test_spotify_api():
    """Testuje główny serwer API"""
    print("\n🎵 Testowanie głównego serwera API...")
    
    try:
        response = requests.get('http://127.0.0.1:5000/current-track', timeout=5)
        if response.status_code == 200:
            print("✅ Główny serwer API odpowiada")
            data = response.json()
            if data.get('track'):
                print(f"   Aktualny utwór: {data['track']} - {data['artist']}")
            else:
                print("   Brak aktywnego utworu")
        elif response.status_code == 204:
            print("✅ Główny serwer API odpowiada (brak aktywnego utworu)")
        else:
            print(f"❌ Główny serwer API nie odpowiada poprawnie: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Nie można połączyć się z głównym serwerem API")
        print("   Upewnij się, że serwer jest uruchomiony: python backend/main.py")
        return False
    except Exception as e:
        print(f"❌ Błąd testowania głównego serwera API: {e}")
        return False
    
    return True

def main():
    print("🎯 Test systemu rozpoznawania gestów Spotify WCAG")
    print("=" * 50)
    
    # Test głównego serwera API
    api_ok = test_spotify_api()
    
    # Test serwera gestów
    gesture_ok = test_gesture_server()
    
    print("\n" + "=" * 50)
    if api_ok and gesture_ok:
        print("✅ Wszystkie testy przeszły pomyślnie!")
        print("🚀 System jest gotowy do użycia")
        print("\n📋 Następne kroki:")
        print("1. Uruchom frontend: cd frontend && npm start")
        print("2. Przejdź do Player w aplikacji")
        print("3. Kliknij 'Włącz gesty'")
        print("4. Wykonaj sekwencję: open-close-open")
    else:
        print("❌ Niektóre testy nie przeszły")
        if not api_ok:
            print("   - Problem z głównym serwerem API")
        if not gesture_ok:
            print("   - Problem z serwerem gestów")
        print("\n🔧 Sprawdź:")
        print("1. Czy wszystkie zależności są zainstalowane")
        print("2. Czy serwery są uruchomione")
        print("3. Czy pliki konfiguracyjne są poprawne")

if __name__ == "__main__":
    main() 