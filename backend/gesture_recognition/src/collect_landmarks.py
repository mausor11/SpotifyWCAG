import cv2
import mediapipe as mp
import pandas as pd
import os
import numpy as np
from pathlib import Path

class HandLandmarkCollector:
    def __init__(self):
        # Inicjalizacja MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=1,
            min_detection_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
    def extract_landmarks_from_image(self, image_path):
        """Wyciąga landmarki z pojedynczego zdjęcia"""
        # Wczytaj obraz
        image = cv2.imread(image_path)
        if image is None:
            print(f"Nie można wczytać obrazu: {image_path}")
            return None
            
        # Konwertuj BGR na RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Przetwórz obraz
        results = self.hands.process(image_rgb)
        
        if results.multi_hand_landmarks:
            # Weź pierwsze wykryte dłonie
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Wyciągnij współrzędne landmarków
            landmarks = []
            for landmark in hand_landmarks.landmark:
                landmarks.extend([landmark.x, landmark.y, landmark.z])
            
            return landmarks
        else:
            print(f"Nie wykryto dłoni w obrazie: {image_path}")
            return None
    
    def process_folder(self, folder_path, label):
        """Przetwarza wszystkie obrazy w folderze i zwraca listę landmarków z etykietami"""
        landmarks_data = []
        folder = Path(folder_path)
        
        # Obsługiwane formaty obrazów
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        
        # Znajdź wszystkie obrazy w folderze
        image_files = []
        for ext in image_extensions:
            image_files.extend(folder.glob(f"*{ext}"))
            image_files.extend(folder.glob(f"*{ext.upper()}"))
        
        print(f"Znaleziono {len(image_files)} obrazów w folderze {folder_path}")
        
        for i, image_path in enumerate(image_files):
            print(f"Przetwarzanie {i+1}/{len(image_files)}: {image_path.name}")
            
            landmarks = self.extract_landmarks_from_image(str(image_path))
            
            if landmarks is not None:
                # Dodaj etykietę na początku
                row_data = [label] + landmarks
                landmarks_data.append(row_data)
            else:
                print(f"Pominięto {image_path.name} - nie wykryto dłoni")
        
        return landmarks_data
    
    def create_dataset(self, data_folder, output_csv_path):
        """Tworzy dataset ze wszystkich folderów z gestami"""
        all_data = []
        
        # Mapowanie nazw folderów na etykiety
        folder_labels = {
            'gesture_close': 'close',
            'gesture_open': 'open', 
            'gesture_pointer': 'pointer'
        }
        
        data_path = Path(data_folder)
        
        for folder_name, label in folder_labels.items():
            folder_path = data_path / folder_name
            if folder_path.exists():
                print(f"\nPrzetwarzanie folderu: {folder_name}")
                folder_data = self.process_folder(folder_path, label)
                all_data.extend(folder_data)
                print(f"Dodano {len(folder_data)} próbek z etykietą '{label}'")
            else:
                print(f"Folder {folder_name} nie istnieje!")
        
        if all_data:
            # Utwórz nagłówki kolumn
            # MediaPipe Hands ma 21 landmarków, każdy z 3 współrzędnymi (x, y, z)
            landmark_columns = []
            for i in range(21):
                landmark_columns.extend([f'landmark_{i}_x', f'landmark_{i}_y', f'landmark_{i}_z'])
            
            columns = ['label'] + landmark_columns
            
            # Utwórz DataFrame
            df = pd.DataFrame(all_data, columns=columns)
            
            # Zapisz do CSV
            df.to_csv(output_csv_path, index=False)
            print(f"\nDataset zapisany do: {output_csv_path}")
            print(f"Łącznie próbek: {len(df)}")
            print(f"Rozkład etykiet:")
            print(df['label'].value_counts())
            
            return df
        else:
            print("Nie udało się wyciągnąć żadnych landmarków!")
            return None
    
    def close(self):
        """Zamyka MediaPipe"""
        self.hands.close()

def main():
    # Ścieżki
    data_folder = "../data"  # Względem lokalizacji tego skryptu
    output_csv = "../data/gestures_dataset.csv"
    
    # Utwórz kolektor
    collector = HandLandmarkCollector()
    
    try:
        # Utwórz dataset
        dataset = collector.create_dataset(data_folder, output_csv)
        
        if dataset is not None:
            print("\nDataset został pomyślnie utworzony!")
            print(f"Wymiary datasetu: {dataset.shape}")
        else:
            print("Nie udało się utworzyć datasetu!")
            
    except Exception as e:
        print(f"Wystąpił błąd: {e}")
    
    finally:
        # Zawsze zamknij MediaPipe
        collector.close()

if __name__ == "__main__":
    main()
