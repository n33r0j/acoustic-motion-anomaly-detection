import csv
import os
import time
import requests
import librosa
import soundfile as sf
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FREESOUND_API_KEY")

if not API_KEY:
    raise RuntimeError("FREESOUND_API_KEY not found in .env")

API_BASE = "https://freesound.org/apiv2"

OUTPUT_DIR = "audio_ml/dataset/anomaly_4class"
METADATA_DIR = os.path.join(OUTPUT_DIR, "metadata")
METADATA_FILE = os.path.join(METADATA_DIR, "metadata.csv")

SAMPLE_RATE = 16000

# Target length of each training clip
CLIP_DURATION = 5

# Test only
SAMPLES_PER_CLASS = 5

SEARCH_QUERIES = {
    "footsteps": [
        "footsteps",
        "walking footsteps",
        "walking",
    ],
    "knocking": [
        "door knock",
        "knocking",
        "knock",
    ],
    "glass_break": [
        "glass breaking",
        "breaking glass",
        "glass break",
    ],
    "normal": [
        "room ambience",
        "house ambience",
        "office ambience",
        "outdoor ambience",
    ],
}


def search_sounds(query, page_size=20):
    """Search FreeSound."""

    url = f"{API_BASE}/search/text/"

    params = {
        "query": query,
        "token": API_KEY,
        "page_size": page_size,
        "fields": (
            "id,name,duration,license,"
            "username,previews"
        ),
    }

    response = requests.get(
        url,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    return response.json().get("results", [])


def download_preview(sound, temp_path):
    """Download FreeSound preview."""

    previews = sound.get("previews", {})

    preview_url = previews.get("preview-hq-mp3")

    if not preview_url:
        preview_url = previews.get("preview-lq-mp3")

    if not preview_url:
        return False

    response = requests.get(
        preview_url,
        timeout=60,
    )

    response.raise_for_status()

    with open(temp_path, "wb") as file:
        file.write(response.content)

    return True


def convert_to_wav(
    input_path,
    output_path,
    class_name,
):
    """
    Convert audio to 16 kHz mono WAV.

    For normal ambience, take a 5-second
    segment from the middle.

    For short anomaly recordings, keep the
    complete recording if it is shorter than
    the target duration.
    """

    audio, sr = librosa.load(
        input_path,
        sr=SAMPLE_RATE,
        mono=True,
    )

    target_samples = SAMPLE_RATE * CLIP_DURATION

    if len(audio) <= target_samples:

        clip = audio

    else:

        if class_name == "normal":
            # Take middle section for ambience.
            start = (
                len(audio) - target_samples
            ) // 2

        else:
            # Initial prototype:
            # take the beginning of the recording.
            start = 0

        clip = audio[
            start:start + target_samples
        ]

    sf.write(
        output_path,
        clip,
        SAMPLE_RATE,
    )


def load_existing_ids():
    """Read already-used FreeSound IDs."""

    ids = set()

    if not os.path.exists(METADATA_FILE):
        return ids

    with open(
        METADATA_FILE,
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            sound_id = row.get("freesound_id")

            if sound_id:
                ids.add(sound_id)

    return ids


def save_metadata(record):

    file_exists = os.path.exists(
        METADATA_FILE
    )

    fieldnames = [
        "freesound_id",
        "class",
        "query",
        "filename",
        "source_name",
        "username",
        "duration",
        "license",
        "source_url",
        "sample_rate",
        "channels",
        "clip_duration",
    ]

    with open(
        METADATA_FILE,
        "a",
        encoding="utf-8",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(record)


def main():

    os.makedirs(
        METADATA_DIR,
        exist_ok=True,
    )

    for class_name in SEARCH_QUERIES:

        os.makedirs(
            os.path.join(
                OUTPUT_DIR,
                class_name,
            ),
            exist_ok=True,
        )

    existing_ids = load_existing_ids()

    print(
        "FreeSound dataset downloader"
    )
    print("============================")

    for class_name, queries in SEARCH_QUERIES.items():

        print(f"\nCLASS: {class_name}")

        class_dir = os.path.join(
            OUTPUT_DIR,
            class_name,
        )

        downloaded = 0

        for query in queries:

            if downloaded >= SAMPLES_PER_CLASS:
                break

            print(f"\nSearching: {query}")

            try:

                results = search_sounds(query)

            except Exception as error:

                print(
                    f"Search failed: {error}"
                )

                continue

            for sound in results:

                if downloaded >= SAMPLES_PER_CLASS:
                    break

                sound_id = str(
                    sound.get("id")
                )

                if not sound_id:
                    continue

                if sound_id in existing_ids:
                    continue

                source_name = sound.get(
                    "name",
                    "unknown",
                )

                duration = float(
                    sound.get(
                        "duration",
                        0,
                    )
                )

                print(
                    f"\nCandidate: "
                    f"{source_name}"
                )

                print(
                    f"Duration: "
                    f"{duration:.1f}s"
                )

                temp_path = os.path.join(
                    class_dir,
                    f"temp_{sound_id}.mp3",
                )

                output_filename = (
                    f"{sound_id}.wav"
                )

                output_path = os.path.join(
                    class_dir,
                    output_filename,
                )

                try:

                    success = download_preview(
                        sound,
                        temp_path,
                    )

                    if not success:

                        print(
                            "No preview available."
                        )

                        continue

                    convert_to_wav(
                        temp_path,
                        output_path,
                        class_name,
                    )

                    os.remove(temp_path)

                    save_metadata({
                        "freesound_id": sound_id,
                        "class": class_name,
                        "query": query,
                        "filename": output_filename,
                        "source_name": source_name,
                        "username": sound.get(
                            "username"
                        ),
                        "duration": duration,
                        "license": sound.get(
                            "license"
                        ),
                        "source_url": (
                            "https://freesound.org/"
                            f"sounds/{sound_id}/"
                        ),
                        "sample_rate": SAMPLE_RATE,
                        "channels": 1,
                        "clip_duration": min(
                            duration,
                            CLIP_DURATION,
                        ),
                    })

                    existing_ids.add(
                        sound_id
                    )

                    downloaded += 1

                    print(
                        f"Saved: "
                        f"{output_filename}"
                    )

                    time.sleep(0.5)

                except Exception as error:

                    print(
                        f"Processing failed: "
                        f"{error}"
                    )

                    if os.path.exists(
                        temp_path
                    ):
                        os.remove(temp_path)

        print(
            f"\n{class_name}: "
            f"{downloaded}/{SAMPLES_PER_CLASS}"
        )

    print(
        "\nDownloader test complete."
    )


if __name__ == "__main__":
    main()