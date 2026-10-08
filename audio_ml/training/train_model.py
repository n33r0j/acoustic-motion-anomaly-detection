import os
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)
import joblib


FEATURE_FILE = "audio_ml/features/X.npy"
LABEL_FILE = "audio_ml/features/y.npy"

MODEL_DIR = "audio_ml/models"
MODEL_FILE = os.path.join(
    MODEL_DIR,
    "acoustic_random_forest.joblib"
)


CLASS_NAMES = [
    "normal",
    "knocking",
    "footsteps",
    "glass_break",
]


# Load features and labels
X = np.load(FEATURE_FILE)
y = np.load(LABEL_FILE)

print("Feature shape:", X.shape)
print("Label shape:", y.shape)


# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# Create model
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)


# Train
print("\nTraining model...")
model.fit(X_train, y_train)


# Predict
y_pred = model.predict(X_test)


# Accuracy
accuracy = accuracy_score(y_test, y_pred)

print("\nAccuracy:", accuracy)


# Detailed performance
print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred,
        target_names=CLASS_NAMES
    )
)


# Confusion matrix
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))


# Save model
os.makedirs(MODEL_DIR, exist_ok=True)

joblib.dump(model, MODEL_FILE)

print("\nModel saved to:")
print(MODEL_FILE)