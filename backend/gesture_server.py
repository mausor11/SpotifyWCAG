from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import cv2
import mediapipe as mp
import numpy as np
from tensorflow.keras.models import load_model
import threading
import time
import os
from api import pause_or_resume, skip_to_next

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Konfiguracja MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)

# Ładowanie modelu
model_path = os.path.join(os.path.dirname(__file__), 'gesture_recognition', 'src', 'model', 'model.h5')
model = load_model(model_path)
labels = ["close", "open", "point"]

# Stan aplikacji
gesture_recognition_active = False
camera = None
gesture_thread = None

# Historia gestów do wykrywania sekwencji
gesture_history = []
MAX_HISTORY = 5
last_gesture_time = 0
GESTURE_COOLDOWN = 0.5  # 500ms przerwy między gestami

def process_gesture_sequence():
    """Analizuje historię gestów i wykrywa sekwencje"""
    if len(gesture_history) < 3:
        return None

    # Sprawdź sekwencję open-close-open
    recent_gestures = gesture_history[-3:]
    if recent_gestures == ['open', 'close', 'open']:
        gesture_history.clear()
        return 'open-close-open'
    if recent_gestures == ['close', 'open', 'close']:
        gesture_history.clear()
        return 'close-open-close'
    
    return None

def add_gesture_to_history(gesture, confidence):
    """Dodaje gest do historii z lepszą logiką"""
    global gesture_history, last_gesture_time
    
    current_time = time.time()
    
    # Dodaj gest tylko jeśli pewność > 0.6 (obniżony próg)
    if confidence < 0.4:
        print(f"❌ Odrzucono gest: {gesture} (pewność: {confidence:.2f} < 0.4)")
        return
    
    # Sprawdź cooldown - nie dodawaj gestów zbyt szybko
    if current_time - last_gesture_time < GESTURE_COOLDOWN:
        print(f"⏰ Cooldown: {gesture} (czekam {GESTURE_COOLDOWN}s)")
        return
    
    # Sprawdź czy to nie jest duplikat ostatniego gestu
    if gesture_history and gesture_history[-1] == gesture:
        print(f"🔄 Duplikat: {gesture} (ostatni: {gesture_history[-1]})")
        return
    
    # Dodaj gest do historii
    gesture_history.append(gesture)
    last_gesture_time = current_time
    
    # Ogranicz historię do 5 ostatnich gestów
    if len(gesture_history) > MAX_HISTORY:
        gesture_history = gesture_history[-MAX_HISTORY:]
    
    print(f"📝 Dodano do historii: {gesture} | Historia: {' → '.join(gesture_history)}")

def gesture_recognition_loop():
    """Główna pętla rozpoznawania gestów"""
    global camera, gesture_recognition_active, gesture_history
    
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("❌ Nie można otworzyć kamery")
        return
    
    print("🎥 Kamera uruchomiona")
    print("🎯 Rozpoznawanie gestów aktywne - czekam na gesty...")
    print("📋 Obsługiwane sekwencje:")
    print("   • open-close-open → Play/Pause")
    print("-" * 50)
    
    while gesture_recognition_active:
        ret, frame = camera.read()
        if not ret:
            continue
            
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Ekstrakcja punktów dłoni
                landmarks = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]).flatten()
                
                # Predykcja gestu
                input_data = landmarks.reshape(1, -1, 1)
                prediction = model.predict(input_data, verbose=0)
                predicted_label = labels[np.argmax(prediction)]
                confidence = np.max(prediction)
                
                # Dodaj gest do historii z lepszą logiką
                add_gesture_to_history(predicted_label, confidence)
                
                # Sprawdź sekwencję gestów
                sequence = process_gesture_sequence()
                if sequence:
                    print(f"🎵 Wykryto sekwencję: {sequence}")
                    handle_gesture_sequence(sequence)
                    # Wyczyść historię po wykryciu sekwencji
                    gesture_history.clear()
                
                # Wyświetl aktualny gest w terminalu
                print(f"🎯 Aktualny gest: {predicted_label} (pewność: {confidence:.2f})")
                
                # Wyślij aktualny gest do frontendu
                socketio.emit('gesture_detected', {
                    'gesture': predicted_label,
                    'confidence': float(confidence),
                    'history': gesture_history
                })
        
        time.sleep(0.1)  # Małe opóźnienie żeby nie przeciążać CPU
    
    if camera:
        camera.release()
    print("-" * 50)
    print("🎥 Kamera zatrzymana")
    print("🎯 Rozpoznawanie gestów wyłączone")

def handle_gesture_sequence(sequence):
    """Obsługuje wykryte sekwencje gestów"""
    if sequence == 'open-close-open':
        print("🎵" + "="*50)
        print("🎵 WYKRYTO SEKWENCJĘ: open-close-open")
        print("🎵 AKCJA: Przełączam play/pause w Spotify")
        print("🎵" + "="*50)
        try:
            pause_or_resume()
            print("✅ Play/pause przełączone pomyślnie!")
            socketio.emit('spotify_action', {
                'action': 'play_pause',
                'message': 'Przełączono play/pause'
            })
        except Exception as e:
            print(f"❌ Błąd przy przełączaniu play/pause: {e}")
    elif sequence == 'close-open-close':
        print("🎵" + "="*50)
        print("🎵 WYKRYTO SEKWENCJĘ: close-open-close")
        print("🎵 AKCJA: Przełączam next w Spotify")
        print("🎵" + "="*50)
        try:
            skip_to_next()
            print("✅ Next przełączone pomyślnie!")
            socketio.emit('spotify_action', {
                'action': 'next',
                'message': 'Przełączono next'
            })
        except Exception as e:
            print(f"❌ Błąd przy przełączaniu next: {e}")

@app.route('/gestures/toggle', methods=['POST'])
def toggle_gesture_recognition():
    """Włącza/wyłącza rozpoznawanie gestów"""
    global gesture_recognition_active, gesture_thread
    
    data = request.get_json()
    enable = data.get('enable', False)
    
    if enable and not gesture_recognition_active:
        gesture_recognition_active = True
        gesture_thread = threading.Thread(target=gesture_recognition_loop)
        gesture_thread.daemon = True
        gesture_thread.start()
        print("🎯 Rozpoznawanie gestów włączone")
        return jsonify({'status': 'enabled', 'message': 'Rozpoznawanie gestów włączone'})
    
    elif not enable and gesture_recognition_active:
        gesture_recognition_active = False
        if gesture_thread:
            gesture_thread.join(timeout=2)
        print("🎯 Rozpoznawanie gestów wyłączone")
        return jsonify({'status': 'disabled', 'message': 'Rozpoznawanie gestów wyłączone'})
    
    return jsonify({'status': 'no_change', 'message': 'Stan nie zmienił się'})

@app.route('/gestures/status', methods=['GET'])
def get_gesture_status():
    """Zwraca status rozpoznawania gestów"""
    return jsonify({
        'active': gesture_recognition_active,
        'history': gesture_history
    })

@socketio.on('connect')
def handle_connect():
    """Obsługa połączenia WebSocket"""
    print(f"🔌 Klient połączony: {request.sid}")
    emit('status', {'message': 'Połączono z serwerem gestów'})

@socketio.on('disconnect')
def handle_disconnect():
    """Obsługa rozłączenia WebSocket"""
    print(f"🔌 Klient rozłączony: {request.sid}")

@socketio.on('toggle_gestures')
def handle_toggle_gestures(data):
    """Obsługa włączania/wyłączania gestów przez WebSocket"""
    enable = data.get('enable', False)
    result = toggle_gesture_recognition()
    emit('gesture_status', result)

if __name__ == '__main__':
    print("🚀 Uruchamianie serwera gestów...")
    socketio.run(app, host='127.0.0.1', port=5001, debug=True) 