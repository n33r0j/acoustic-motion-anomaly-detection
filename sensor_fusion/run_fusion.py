import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from audio_ml.inference.predict import predict
from sensor_fusion.fusion import sensor_fusion


if len(sys.argv) != 3:
    print("Usage:")
    print("python3 sensor_fusion/run_fusion.py <audio.wav> <motion>")
    sys.exit(1)


audio_file = sys.argv[1]
motion = int(sys.argv[2])

acoustic_event, confidence = predict(audio_file)

result = sensor_fusion(
    acoustic_event,
    confidence,
    motion
)

print("\n--- SENSOR FUSION RESULT ---")
print(f"Acoustic event: {result['acoustic_event']}")
print(f"Confidence:     {result['confidence']:.2f}")
print(f"Motion:         {result['motion']}")
print(f"Result:         {result['result']}")
print(f"Severity:       {result['severity']}")