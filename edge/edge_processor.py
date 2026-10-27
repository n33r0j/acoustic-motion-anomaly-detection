import serial
import wave
import struct
import time
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from audio_ml.inference.predict import predict
from sensor_fusion.fusion import sensor_fusion
from cloud.mqtt_client import connect_mqtt, publish_event

PORT = "/dev/cu.usbserial-10"
BAUD_RATE = 460800

SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2  # int16 = 2 bytes

OUTPUT_DIR = Path("edge/audio_events")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
JSON_DIR = Path("edge/event_json")
JSON_DIR.mkdir(parents=True, exist_ok=True)

motion = 0
ser = serial.Serial(
    PORT,
    BAUD_RATE,
    timeout=2
)
mqtt_connection = connect_mqtt()
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

        new_motion = int(
            line.split(":")[1]
        )

        if new_motion != motion:
            motion = new_motion
            print(f"Motion changed: {motion}")  

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
        # -----------------------------
        # Acoustic ML prediction
        # -----------------------------

        acoustic_event, confidence = predict(str(filename))

        print("\n--- ACOUSTIC PREDICTION ---")
        print(f"Event:      {acoustic_event}")
        print(f"Confidence: {confidence:.2f}")
        # -----------------------------
        # Sensor fusion
        # -----------------------------

        fusion_result = sensor_fusion(
            acoustic_event,
            confidence,
            motion
        )

        print("\n--- SENSOR FUSION RESULT ---")
        print(f"Acoustic event: {fusion_result['acoustic_event']}")
        print(f"Confidence:     {fusion_result['confidence']:.2f}")
        print(f"Motion:         {fusion_result['motion']}")
        print(f"Result:         {fusion_result['result']}")
        print(f"Severity:       {fusion_result['severity']}")
        # -----------------------------
        # Create event JSON
        # -----------------------------

        event_data = {
            "event_id": f"evt-{timestamp}-001",
            "timestamp": timestamp,
            "acoustic_event": fusion_result["acoustic_event"],
            "confidence": round(fusion_result["confidence"], 2),
            "motion": fusion_result["motion"],
            "result": fusion_result["result"],
            "severity": fusion_result["severity"]
        }

        json_filename = (
            JSON_DIR /
            f"event_{timestamp}.json"
        )

        with open(json_filename, "w") as json_file:
            json.dump(event_data, json_file, indent=2)

        print(f"JSON saved: {json_filename}")
        publish_event(
            mqtt_connection,
            event_data
     )