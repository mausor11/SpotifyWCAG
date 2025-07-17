import pandas as pd
from sklearn.preprocessing import StandardScaler

# Wczytaj dane
df = pd.read_csv("../data/gestures_dataset_augmented.csv")

# Oddziel etykiety od danych
X = df.drop("label", axis=1)
y = df["label"]

# Normalizacja StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Składanie w DataFrame
normalized_df = pd.DataFrame(X_scaled, columns=X.columns)
normalized_df.insert(0, "label", y.values)

# Zapis do pliku
normalized_df.to_csv("gestures_dataset_normalized.csv", index=False)
print("✅ Zapisano do gestures_dataset_normalized.csv")
