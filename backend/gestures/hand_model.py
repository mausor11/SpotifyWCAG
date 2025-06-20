import cv2
import mediapipe as mp
import numpy as np
import pickle

# === ŁADOWANIE MODELU I SKALERA ===
with open("gesture_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

with open("label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

# === MEDIAPIPE ===
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

# === KAMERA ===
cap = cv2.VideoCapture(0)

def extract_landmarks(hand_landmarks, frame_shape):
    h, w, _ = frame_shape
    data = []
    for lm in hand_landmarks.landmark:
        data.extend([lm.x, lm.y, lm.z])
    return data

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    gesture_text = "No hand"

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Pobierz i przekształć landmarki
            landmark_data = extract_landmarks(hand_landmarks, frame.shape)
            landmark_data = np.array(landmark_data).reshape(1, -1)
            landmark_data_scaled = scaler.transform(landmark_data)

            # Predykcja
            prediction = model.predict(landmark_data_scaled)
            label = label_encoder.inverse_transform(prediction)[0]
            gesture_text = f"Detected: {label}"

    # Wyświetlenie na kamerze
    cv2.putText(frame, gesture_text, (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    cv2.imshow("Gesture Prediction", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
