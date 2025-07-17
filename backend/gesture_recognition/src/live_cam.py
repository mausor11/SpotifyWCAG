import cv2
import mediapipe as mp
import numpy as np
from tensorflow.keras.models import load_model

model = load_model("model/model.h5")
labels = ["close", "open", "point"]

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
        # Rysowanie dłoni
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Ekstrakcja 21 punktów (x, y, z)
            landmarks = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]).flatten()

            # Normalizacja taka jak przy trenowaniu (u Ciebie był StandardScaler)
            # Jeśli chcesz użyć dokładnie tego samego przelicznika – zapisz scaler i użyj: scaler.transform(...)
            # Na razie przyjmujemy, że dane są wystarczająco wystandaryzowane "na żywo"
            
            # Zmiana shape i predykcja
            input_data = landmarks.reshape(1, -1, 1)  # (1, 63, 1) – jak w CNN
            prediction = model.predict(input_data)
            predicted_label = labels[np.argmax(prediction)]

            # Wyświetlenie wyniku
            cv2.putText(frame, f"Gesture: {predicted_label}", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

    # Pokaż obraz
    cv2.imshow("Gesture Recognition", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC = wyjście
        break

cap.release()
cv2.destroyAllWindows()