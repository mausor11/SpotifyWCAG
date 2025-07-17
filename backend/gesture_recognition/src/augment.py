import pandas as pd 
import numpy as np

df = pd.read_csv("../data/gestures_dataset.csv")

def add_noise(landmarks, noise_level=0.01):
    noise = np.random.normal(0, noise_level, landmarks.shape)
    return landmarks + noise

def add_shift(landmarks, shift_range=0.05):
    shift = np.random.uniform(-shift_range, shift_range, landmarks.shape)
    return landmarks + shift

def add_scale(landmarks, scale_range=0.1):
    scale = 1 + np.random.uniform(-scale_range, scale_range)
    return landmarks * scale

def rotate_z(landmarks, angle_range=np.pi / 8):
    angle = np.random.uniform(-angle_range, angle_range)
    cos_a, sin_a = np.cos(angle), np.sin(angle)
    rotation_matrix = np.array([
        [cos_a, -sin_a, 0],
        [sin_a,  cos_a, 0],
        [0,      0,     1]
    ])
    return landmarks @ rotation_matrix.T


landmark_cols = [col for col in df.columns if col.startswith('landmark')]
labels = df['label'].values
landmarks = df[landmark_cols].values.reshape((-1, 21, 3))

augmented_landmarks = []
augmented_labels = []

for lm, label in zip(landmarks, labels):
    for _ in range(2):  # liczba kopii augmentacji
        aug = lm.copy()
        aug = add_noise(aug)
        aug = add_shift(aug)
        aug = add_scale(aug)
        aug = rotate_z(aug)
        augmented_landmarks.append(aug)
        augmented_labels.append(label)

all_landmarks = np.concatenate([landmarks, np.array(augmented_landmarks)], axis=0)
all_labels = np.concatenate([labels, np.array(augmented_labels)], axis=0)

flat_landmarks = all_landmarks.reshape((all_landmarks.shape[0], -1))
augmented_df = pd.DataFrame(flat_landmarks, columns=landmark_cols)
augmented_df.insert(0, 'label', all_labels)

augmented_df.to_csv("gestures_dataset_augmented.csv", index=False)