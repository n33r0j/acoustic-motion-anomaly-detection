import os
import time
import numpy as np
import sounddevice as sd
import soundfile as sf


# ============================================================
# Configuration
# ============================================================

OUTPUT_DIR = (
    "/Users/mac_nrj/acoustic-motion-anomaly-detection/"
    "audio_ml/dataset/anomaly_4class/footsteps"
)

SAMPLE_RATE = 16000
CHANNELS = 1
DURATION = 5

# Set to None to use the system default input.
# If needed, replace with your microphone/input device number.
DEVICE = None

# Number of recordings to make
NUM_RECORDINGS = 30


# ============================================================
# Create output directory
# ============================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_next_file_number():
    """
    Find the next available recording number.
    """

    existing_files = [
        filename
        for filename in os.listdir(OUTPUT_DIR)
        if filename.startswith("footstep_")
        and filename.endswith(".wav")
    ]

    numbers = []

    for filename in existing_files:
        try:
            number = int(
                filename.replace("footstep_", "")
                .replace(".wav", "")
            )
            numbers.append(number)
        except ValueError:
            pass

    if not numbers:
        return 1

    return max(numbers) + 1


def record_audio():

    file_number = get_next_file_number()

    print("=" * 60)
    print("INMP441 Footstep Dataset Recorder")
    print("=" * 60)

    print(f"Output directory:")
    print(OUTPUT_DIR)

    print()
    print(f"Sample rate : {SAMPLE_RATE} Hz")
    print(f"Channels    : {CHANNELS} (mono)")
    print(f"Duration    : {DURATION} seconds")
    print(f"Recordings  : {NUM_RECORDINGS}")

    print()
    print("Instructions:")
    print("1. Prepare the footstep sound.")
    print("2. Press ENTER.")
    print("3. Wait for the countdown.")
    print("4. Perform/play the footstep sound.")
    print("5. Recording lasts exactly 5 seconds.")
    print()

    for i in range(NUM_RECORDINGS):

        current_number = file_number + i

        filename = f"footstep_{current_number:03d}.wav"
        filepath = os.path.join(OUTPUT_DIR, filename)

        input(
            f"\nPress ENTER to record "
            f"{i + 1}/{NUM_RECORDINGS}..."
        )

        print("Get ready...")

        time.sleep(1)

        print("3...")
        time.sleep(1)

        print("2...")
        time.sleep(1)

        print("1...")
        time.sleep(1)

        print("🔴 RECORDING")

        try:

            audio = sd.rec(
                int(DURATION * SAMPLE_RATE),
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype="float32",
                device=DEVICE
            )

            sd.wait()

            print("Recording finished.")

            # Make sure the audio is mono
            if audio.ndim > 1:
                audio = audio[:, 0]

            # Save as 16 kHz mono WAV
            sf.write(
                filepath,
                audio,
                SAMPLE_RATE,
                subtype="PCM_16"
            )

            print(f"Saved:")
            print(filepath)

        except Exception as e:

            print("ERROR while recording:")
            print(e)

    print()
    print("=" * 60)
    print("Recording session complete.")
    print("=" * 60)


if __name__ == "__main__":
    record_audio()