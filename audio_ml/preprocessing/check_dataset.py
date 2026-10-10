import pandas as pd

DATASET_CSV = "audio_ml/dataset/ESC-50/meta/esc50.csv"

df = pd.read_csv(DATASET_CSV)

print("Total audio files:", len(df))
print()

print("Available classes:")
print(df["category"].unique())

print()
print("Number of samples per class:")
print(df["category"].value_counts())