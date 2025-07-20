import speech_recognition as sr
import threading
import time
from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Spotify API configuration
SPOTIFY_API_BASE = "https://api.spotify.com/v1"
SPOTIFY_TOKEN = os.getenv('SPOTIFY_TOKEN')

class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self.microphone = None
        self.listen_thread = None
        
    def start_listening(self):
        if self.is_listening:
            return
            
        self.is_listening = True
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
        self.listen_thread = threading.Thread(target=self._listen_loop)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        
    def stop_listening(self):
        self.is_listening = False
        if self.listen_thread:
            self.listen_thread.join(timeout=1)
            
    def _listen_loop(self):
        while self.is_listening:
            try:
                with self.microphone as source:
                    print("🎤 Nasłuchiwanie komend...")
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                    try:
                        command = self.recognizer.recognize_google(audio, language="pl-PL")
                        print(f"🔍 Rozpoznano: {command}")
                        
                        # Process command
                        action = self._process_command(command.lower())
                        if action:
                            print(f"🎵 Wykonuję akcję: {action}")
                            socketio.emit('speech_command', action)
                        else:
                            print(f"❌ Nie rozpoznano akcji dla komendy: {command}")
                            
                    except sr.UnknownValueError:
                        print("❌ Nie rozpoznano mowy")
                    except sr.RequestError as e:
                        print(f"❌ Błąd API: {e}")
                        
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                print(f"❌ Błąd nasłuchiwania: {e}")
                time.sleep(1)
                
    def _process_command(self, command):
        """Process voice commands and return Spotify actions"""
        
        # Next track commands
        if any(word in command for word in ['następny', 'następna', 'dalej', 'skip', 'next']):
            return {'action': 'next'}
            
        # Previous track commands
        if any(word in command for word in ['poprzedni', 'poprzednia', 'wstecz', 'back', 'previous']):
            return {'action': 'previous'}
            
        # Play specific song - sprawdź najpierw czy to nie jest konkretna piosenka
        if 'graj' in command or 'play' in command:
            # Extract song title from command
            song_title = self._extract_song_title(command)
            if song_title and len(song_title) > 2:  # Jeśli jest tytuł piosenki
                return {'action': 'play_song', 'song': song_title}
        
        # Play/pause commands - tylko jeśli nie ma konkretnej piosenki
        if any(word in command for word in ['graj', 'play', 'start', 'odtwarzaj']):
            return {'action': 'play'}
            
        if any(word in command for word in ['pauza', 'pause', 'stop', 'zatrzymaj']):
            return {'action': 'pause'}
                
        return None
        
    def _extract_song_title(self, command):
        """Extract song title from command"""
        # Remove common words
        words_to_remove = ['graj', 'play', 'utwór', 'piosenkę', 'piosenka', 'tytuł']
        for word in words_to_remove:
            command = command.replace(word, '').strip()
        print(f"🎵 Wyekstrahowany tytuł: '{command}'")
        return command if command else None

# Initialize speech recognizer
speech_recognizer = SpeechRecognizer()

@socketio.on('connect')
def handle_connect():
    print("🔌 Klient połączony z serwerem mowy")
    emit('connected', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    print("🔌 Klient rozłączony z serwera mowy")

@socketio.on('start_speech')
def handle_start_speech():
    print("🎤 Uruchamianie rozpoznawania mowy")
    speech_recognizer.start_listening()
    emit('speech_status', {'status': 'started'})

@socketio.on('stop_speech')
def handle_stop_speech():
    print("🛑 Zatrzymywanie rozpoznawania mowy")
    speech_recognizer.stop_listening()
    emit('speech_status', {'status': 'stopped'})

if __name__ == '__main__':
    print("🎤 Serwer rozpoznawania mowy uruchamiany na porcie 5002")
    socketio.run(app, host='0.0.0.0', port=5002, debug=True) 