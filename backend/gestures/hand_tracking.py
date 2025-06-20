import cv2
import mediapipe as mp
import math
import requests
API_URL = "http://127.0.0.1:5000/set-volume"

cap = cv2.VideoCapture(0)
hands = mp.solutions.hands.Hands(max_num_hands=1)  # tylko jedna dłoń
draw = mp.solutions.drawing_utils

prev_volume = -1

while True:
    ret, frame = cap.read()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            draw.draw_landmarks(frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)

            h, w, _ = frame.shape

            # Rysowanie numerów landmarków
            for idx, lm in enumerate(hand_landmarks.landmark):
                x, y = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (x, y), 4, (0, 255, 255), -1)
                cv2.putText(frame, str(idx), (x + 5, y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # Landmarky 4 (kciuk) i 8 (wskazujący)
            lm_thumb = hand_landmarks.landmark[4]
            lm_index = hand_landmarks.landmark[8]

            x1, y1 = int(lm_thumb.x * w), int(lm_thumb.y * h)
            x2, y2 = int(lm_index.x * w), int(lm_index.y * h)



            # Odległość i jej wyświetlenie
            distance = int(math.hypot(x2 - x1, y2 - y1))
            mid_x = (x1 + x2) // 2
            mid_y = (y1 + y2) // 2 - 10
            if distance < 500:
                # Rysuj linię między punktami
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{distance/5}%", (mid_x, mid_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # Mapowanie na głośność (0–100%)
            if distance <= 500:
                volume_percent = int((distance / 500) * 100)
                if volume_percent != prev_volume:
                    try:
                        requests.put(f"{API_URL}?volume_percent={volume_percent}")
                        prev_volume = volume_percent
                        print(f"🔊 Głośność: {volume_percent}%")
                    except Exception as e:
                        print("❌ Błąd ustawiania głośności:", e)

    cv2.imshow("Sterowanie głośnością: Kciuk – Wskazujący", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
