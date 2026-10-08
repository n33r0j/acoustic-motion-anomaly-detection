import os
import numpy as np
import librosa


DATASET_DIR = "audio_ml/dataset/project_audio"
FEATURE_DIR = "audio_ml/features"

SAMPLE_RATE = 16000
N_MFCC = 40


CLASS_NAMES = [
    "normal",
    "knocking",
    "footsteps",
    "glass_break",
]


def extract_features(file_path):
    """
    Load an audio file and extract MFCC features.
    """

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

    # Convert variable-length audio into fixed-size features
    mfcc_mean = np.mean(mfcc, axis=1)
    mfcc_std = np.std(mfcc, axis=1)

    features = np.concatenate([
        mfcc_mean,
        mfcc_std
    ])

    return features


def main():

    os.makedirs(FEATURE_DIR, exist_ok=True)

    X = []
    y = []

    for label, class_name in enumerate(CLASS_NAMES):

        class_dir = os.path.join(
            DATASET_DIR,
            class_name
        )

        print(f"\nProcessing class: {class_name}")

        for filename in sorted(os.listdir(class_dir)):

            if not filename.endswith(".wav"):
                continue

            file_path = os.path.join(
                class_dir,
                filename
            )

            try:
                features = extract_features(file_path)

                X.append(features)
                y.append(label)

            except Exception as e:
                print(f"Error processing {filename}: {e}")

    X = np.array(X)
    y = np.array(y)

    np.save(
        os.path.join(FEATURE_DIR, "X.npy"),
        X
    )

    np.save(
        os.path.join(FEATURE_DIR, "y.npy"),
        y
    )

    print("\nMFCC extraction complete!")
    print("Feature shape:", X.shape)
    print("Label shape:", y.shape)


if __name__ == "__main__":
    main()