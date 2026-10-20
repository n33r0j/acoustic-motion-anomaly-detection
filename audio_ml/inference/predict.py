import os
import sys

import joblib
import librosa
import numpy as np


MODEL_FILE = "audio_ml/models/acoustic_random_forest.joblib"

SAMPLE_RATE = 16000
N_MFCC = 40

CLASS_NAMES = [
    "normal",
    "knocking",
    "footsteps",
    "glass_break",
]


def extract_features(file_path):
    """Extract the same MFCC features used during training."""

    audio, sr = librosa.load(
        file_path,
        sr=SAMPLE_RATE,
        mono=True
    )

    mfcc = librosa.feature.mfcc(
        y=audio,
        sr=sr,
        n_mfcc=N_MFCC
    )

    mfcc_mean = np.mean(mfcc, axis=1)
    mfcc_std = np.std(mfcc, axis=1)

    return np.concatenate([
        mfcc_mean,
        mfcc_std
    ])


def predict(file_path):

    if not os.path.exists(file_path):
        print(f"Audio file not found: {file_path}")
        return

    # Load trained model
    model = joblib.load(MODEL_FILE)

    # Extract features
    features = extract_features(file_path)

    # Model expects one sample with shape (1, 80)
    features = features.reshape(1, -1)

    # Predict class
    prediction = model.predict(features)[0]

    # Get probability for each class
    probabilities = model.predict_proba(features)[0]

    predicted_class = CLASS_NAMES[prediction]
    confidence = probabilities[prediction]

    print("\nAudio file:", file_path)
    print("Predicted class:", predicted_class)
    print(f"Confidence: {confidence:.2f}")

    print("\nClass probabilities:")

    for class_name, probability in zip(
        CLASS_NAMES,
        probabilities
    ):
        print(f"  {class_name}: {probability:.2f}")

    return predicted_class, confidence


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage:")
        print(
            "python3 audio_ml/inference/predict.py "
            "<audio_file.wav>"
        )
        sys.exit(1)

    predict(sys.argv[1])