import serial
import wave
import struct
import time
from pathlib import Path

PORT = "/dev/cu.usbserial-10"
BAUD_RATE = 460800

SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2  # int16 = 2 bytes

OUTPUT_DIR = Path("edge/audio_events")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ser = serial.Serial(
    PORT,
    BAUD_RATE,
    timeout=2
)

print("Connected to ESP32")
print("Waiting for audio events...")

while True:

    line = ser.readline().decode(
        errors="ignore"
    ).strip()

    if not line:
        continue

    # -----------------------------
    # PIR status
    # -----------------------------

    if line.startswith("MOTION:"):

        motion = int(
            line.split(":")[1]
        )

        print(f"Motion: {motion}")

    # -----------------------------
    # Audio event
    # -----------------------------

    elif line == "AUDIO_START":

        print("Audio event received")

        audio_samples = []

        while True:

            audio_line = ser.readline().decode(
                errors="ignore"
            ).strip()

            if audio_line == "AUDIO_END":
                break

            try:
                sample = int(audio_line)
                audio_samples.append(sample)

            except ValueError:
                continue

        print(
            f"Received {len(audio_samples)} samples"
        )

        # -----------------------------
        # Save WAV
        # -----------------------------

        timestamp = int(time.time())

        filename = (
            OUTPUT_DIR /
            f"event_{timestamp}.wav"
        )

        with wave.open(str(filename), "wb") as wav:

            wav.setnchannels(CHANNELS)
            wav.setsampwidth(SAMPLE_WIDTH)
            wav.setframerate(SAMPLE_RATE)

            frames = b"".join(
                struct.pack("<h", sample)
                for sample in audio_samples
            )

            wav.writeframes(frames)

        print(
            f"Saved: {filename}"
        )