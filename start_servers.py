#!/usr/bin/env python3

import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

class ServerManager:
    def __init__(self):
        self.processes = {}
        self.running = True
        
        self.project_root = Path(__file__).parent.absolute()
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        
        self.servers = {
            "auth_server": {
                "command": [sys.executable, "auth_server.py"],
                "cwd": self.backend_dir,
                "port": 8888,
                "description": "Spotify Auth Server"
            },
            "speech_server": {
                "command": [sys.executable, "speech_server.py"],
                "cwd": self.backend_dir,
                "port": 5001,
                "description": "Speech Recognition Server"
            },
            "gesture_server": {
                "command": [sys.executable, "gesture_server.py"],
                "cwd": self.backend_dir,
                "port": 5002,
                "description": "Gesture Recognition Server"
            },
            "main_server": {
                "command": [sys.executable, "main.py"],
                "cwd": self.backend_dir,
                "port": 5000,
                "description": "Main API Server"
            },
            "frontend": {
                "command": ["npm", "start"],
                "cwd": self.frontend_dir,
                "port": 3000,
                "description": "React Frontend"
            }
        }
        
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        print(f"\n🛑 Otrzymano sygnał {signum}. Zatrzymuję wszystkie serwery...")
        self.stop_all_servers()
        sys.exit(0)
    
    def check_dependencies(self):
        print("🔍 Sprawdzanie zależności...")
        
        if not self.backend_dir.exists():
            print(f"❌ Katalog backend nie istnieje: {self.backend_dir}")
            return False
        
        if not self.frontend_dir.exists():
            print(f"❌ Katalog frontend nie istnieje: {self.frontend_dir}")
            return False
        
        required_files = ["auth_server.py", "speech_server.py", "gesture_server.py", "main.py"]
        for file in required_files:
            file_path = self.backend_dir / file
            if not file_path.exists():
                print(f"❌ Plik {file} nie istnieje w katalogu backend")
                return False
        
        if not (self.frontend_dir / "package.json").exists():
            print(f"❌ package.json nie istnieje w katalogu frontend")
            return False
        
        if not (self.frontend_dir / "node_modules").exists():
            print("⚠️  node_modules nie istnieje. Uruchamiam npm install...")
            try:
                subprocess.run(["npm", "install"], cwd=self.frontend_dir, check=True)
                print("✅ npm install zakończony pomyślnie")
            except subprocess.CalledProcessError as e:
                print(f"❌ Błąd podczas npm install: {e}")
                return False
        
        print("✅ Wszystkie zależności są dostępne")
        return True
    
    def start_server(self, server_name, config):
        try:
            print(f"🚀 Uruchamiam {config['description']}...")
            
            process = subprocess.Popen(
                config["command"],
                cwd=config["cwd"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes[server_name] = process
            
            time.sleep(2)
            
            if process.poll() is None:
                print(f"✅ {config['description']} uruchomiony (PID: {process.pid})")
                return True
            else:
                print(f"❌ {config['description']} nie uruchomił się poprawnie")
                return False
                
        except Exception as e:
            print(f"❌ Błąd podczas uruchamiania {config['description']}: {e}")
            return False
    
    def start_all_servers(self):
        print("🎵 Uruchamiam Spotify WCAG Application...")
        print("=" * 50)
        
        server_order = ["auth_server", "main_server", "speech_server", "gesture_server", "frontend"]
        
        for server_name in server_order:
            if server_name in self.servers:
                config = self.servers[server_name]
                if not self.start_server(server_name, config):
                    print(f"❌ Nie udało się uruchomić {config['description']}")
                    self.stop_all_servers()
                    return False
                
                if server_name == "frontend":
                    time.sleep(5)
                else:
                    time.sleep(3)
        
        return True
    
    def monitor_processes(self):

        print("\n📊 Monitorowanie procesów...")
        print("=" * 50)
        
        while self.running:
            all_running = True
            
            for server_name, process in self.processes.items():
                if process.poll() is not None:
                    print(f"❌ {self.servers[server_name]['description']} zatrzymał się nieoczekiwanie")
                    all_running = False
                    break
            
            if not all_running:
                break
            
            time.sleep(5)
        
        if not all_running:
            print("🛑 Jeden z serwerów zatrzymał się. Zatrzymuję wszystkie...")
            self.stop_all_servers()
    
    def stop_all_servers(self):
        print("\n🛑 Zatrzymuję wszystkie serwery...")
        
        for server_name, process in self.processes.items():
            if process.poll() is None:
                print(f"🛑 Zatrzymuję {self.servers[server_name]['description']}...")
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"⚠️  Wymuszam zatrzymanie {self.servers[server_name]['description']}...")
                    process.kill()
                except Exception as e:
                    print(f"❌ Błąd podczas zatrzymywania {self.servers[server_name]['description']}: {e}")
        
        self.processes.clear()
        print("✅ Wszystkie serwery zatrzymane")
    
    def print_status(self):
        print("\n📊 Status serwerów:")
        print("=" * 30)
        
        for server_name, process in self.processes.items():
            status = "🟢 Uruchomiony" if process.poll() is None else "🔴 Zatrzymiony"
            print(f"{self.servers[server_name]['description']}: {status}")
    
    def run(self):
        print("🎵 Spotify WCAG Application Startup Script")
        print("=" * 50)
        
        if not self.check_dependencies():
            return False
        
        if not self.start_all_servers():
            return False
        
        self.print_status()
        
        print("\n🎉 Wszystkie serwery uruchomione pomyślnie!")
        print("=" * 50)
        print("🌐 Frontend: http://localhost:3000")
        print("🔧 Main API: http://localhost:5000")
        print("🎤 Speech Server: http://localhost:5001")
        print("👋 Gesture Server: http://localhost:5002")
        print("\n💡 Naciśnij Ctrl+C aby zatrzymać wszystkie serwery")
        print("=" * 50)
        
        try:
            self.monitor_processes()
        except KeyboardInterrupt:
            print("\n🛑 Otrzymano Ctrl+C")
            self.stop_all_servers()
        
        return True

def main():
    manager = ServerManager()
    success = manager.run()
    
    if success:
        print("✅ Aplikacja zakończona pomyślnie")
    else:
        print("❌ Aplikacja zakończona z błędami")
        sys.exit(1)

if __name__ == "__main__":
    main() 