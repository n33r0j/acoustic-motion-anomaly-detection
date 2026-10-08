import os
import shutil
import pandas as pd


# Paths
CSV_PATH = "audio_ml/dataset/ESC-50/meta/esc50.csv"
AUDIO_DIR = "audio_ml/dataset/ESC-50/audio"
OUTPUT_DIR = "audio_ml/dataset/project_audio"


# ESC-50 class → our project class
CLASS_MAPPING = {
    "rain": "normal",
    "door_wood_knock": "knocking",
    "footsteps": "footsteps",
    "glass_breaking": "glass_break",
}


# Read metadata
df = pd.read_csv(CSV_PATH)


# Create output folders
for project_class in CLASS_MAPPING.values():
    os.makedirs(
        os.path.join(OUTPUT_DIR, project_class),
        exist_ok=True
    )


# Copy selected audio files
for esc50_class, project_class in CLASS_MAPPING.items():

    class_files = df[df["category"] == esc50_class]

    print(
        f"{esc50_class} -> {project_class}: "
        f"{len(class_files)} files"
    )

    for filename in class_files["filename"]:

        source = os.path.join(AUDIO_DIR, filename)

        destination = os.path.join(
            OUTPUT_DIR,
            project_class,
            filename
        )

        shutil.copy2(source, destination)


print("\nDataset preparation complete!")
print(f"Output directory: {OUTPUT_DIR}")