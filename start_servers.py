#!/usr/bin/env python3
"""
Skrypt do uruchamiania obu serwerów:
1. Główny serwer API (port 5000)
2. Serwer gestów (port 5001)
"""

import subprocess
import sys
import time
import os
from threading import Thread

def run_server(script_path, port, name):
    """Uruchamia serwer w osobnym procesie"""
    try:
        print(f"🚀 Uruchamianie {name} na porcie {port}...")
        process = subprocess.Popen([sys.executable, script_path], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        print(f"✅ {name} uruchomiony (PID: {process.pid})")
        
        # Wyświetl logi w czasie rzeczywistym
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"[{name}] {output.strip()}")
                
    except Exception as e:
        print(f"❌ Błąd uruchamiania {name}: {e}")

def main():
    # Sprawdź czy jesteśmy w odpowiednim katalogu
    if not os.path.exists('backend'):
        print("❌ Uruchom skrypt z głównego katalogu projektu")
        sys.exit(1)
    
    # Ścieżki do skryptów
    main_server = os.path.join('backend', 'main.py')
    gesture_server = os.path.join('backend', 'gesture_server.py')
    
    # Sprawdź czy pliki istnieją
    if not os.path.exists(main_server):
        print(f"❌ Nie znaleziono {main_server}")
        sys.exit(1)
    
    if not os.path.exists(gesture_server):
        print(f"❌ Nie znaleziono {gesture_server}")
        sys.exit(1)
    
    print("🎵 Uruchamianie serwerów Spotify WCAG...")
    print("=" * 50)
    
    # Uruchom serwery w osobnych wątkach
    main_thread = Thread(target=run_server, args=(main_server, 5000, "API Server"))
    gesture_thread = Thread(target=run_server, args=(gesture_server, 5001, "Gesture Server"))
    
    main_thread.daemon = True
    gesture_thread.daemon = True
    
    main_thread.start()
    time.sleep(2)  # Krótkie opóźnienie między uruchomieniami
    gesture_thread.start()
    
    print("=" * 50)
    print("✅ Oba serwery uruchomione!")
    print("📱 Frontend: http://localhost:3000")
    print("🔌 API: http://localhost:5000")
    print("🎯 Gestures: http://localhost:5001")
    print("=" * 50)
    print("Naciśnij Ctrl+C aby zatrzymać wszystkie serwery")
    
    try:
        # Czekaj na zakończenie
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Zatrzymywanie serwerów...")
        sys.exit(0)

if __name__ == "__main__":
    main() 