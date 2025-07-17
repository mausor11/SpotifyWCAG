import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, Dense, Dropout, Flatten
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

# === 1. Wczytanie i przygotowanie danych ===
df = pd.read_csv("../data/gestures_dataset_normalized.csv")
X = df.drop("label", axis=1).values
y = df["label"].values

# Kodowanie etykiet
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)
y_onehot = to_categorical(y_encoded)

X_cnn = X.reshape((-1, X.shape[1], 1))


# === 3. Podział na zbiór treningowy i testowy ===
X_train, X_test, y_train, y_test = train_test_split(X_cnn, y_onehot, test_size=0.2, random_state=42)

# === 4. Model CNN + LSTM ===
model = Sequential()
model.add(Conv1D(64, kernel_size=3, activation='relu', input_shape=(63, 1)))
model.add(Dropout(0.3))
model.add(Flatten())
model.add(Dense(64, activation='relu'))
model.add(Dense(y_train.shape[1], activation='softmax'))

# === 5. Trening ===
early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
history = model.fit(X_train, y_train,
          epochs=25, batch_size=32,
          validation_data=(X_test, y_test),
          callbacks=[early_stop])

# === 6. Ewaluacja ===
loss, acc = model.evaluate(X_test, y_test)
print(f"\n🎯 Dokładność na zbiorze testowym: {acc:.2f}")

model.save("model.h5")

plt.plot(history.history['loss'], label='train')
plt.plot(history.history['val_loss'], label='val')
plt.legend(); plt.title('Loss'); plt.show()

y_pred = model.predict(X_test)
y_pred_classes = np.argmax(y_pred, axis=1)
y_true_classes = np.argmax(y_test, axis=1)

cm = confusion_matrix(y_true_classes, y_pred_classes)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=encoder.classes_)
disp.plot(cmap=plt.cm.Blues)
plt.title("Confusion Matrix")
plt.show()

