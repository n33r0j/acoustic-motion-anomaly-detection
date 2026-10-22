from awscrt import mqtt
from awsiot import mqtt_connection_builder
import time
import json
from pathlib import Path

# --------------------------------------------------
# AWS IoT Core
# --------------------------------------------------

ENDPOINT = "a1vjopesjlu532-ats.iot.ap-south-1.amazonaws.com"

# macOS certificate folder
CERT_FOLDER = Path(
    r"/Users/mac_nrj/Downloads/cloud_certificate"
)

CERTIFICATE = CERT_FOLDER / (
    "e374e1cd76dda67582d7d83e8cb6acca9b9aeca63a6fbb6e846b01a1cc9ff470"
    "-certificate.pem.crt"
)

PRIVATE_KEY = CERT_FOLDER / (
    "e374e1cd76dda67582d7d83e8cb6acca9b9aeca63a6fbb6e846b01a1cc9ff470"
    "-private.pem.key"
)

ROOT_CA = CERT_FOLDER / "AmazonRootCA1.pem"

CLIENT_ID = "laptop-anomaly-client"

TOPIC = "esp32/anomaly/events"


# --------------------------------------------------
# JSON event file
# --------------------------------------------------

JSON_FILE = Path(
    r"edge/event_json/event_1792684340.json"
)


# --------------------------------------------------
# Check JSON file
# --------------------------------------------------

if not JSON_FILE.exists():
    print(f"JSON file not found: {JSON_FILE}")
    exit(1)


# --------------------------------------------------
# Read JSON file
# --------------------------------------------------

with open(JSON_FILE, "r") as json_file:
    event = json.load(json_file)


print("JSON event loaded:")
print(json.dumps(event, indent=2))


# --------------------------------------------------
# MQTT connection
# --------------------------------------------------

mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=ENDPOINT,
    port=8883,
    cert_filepath=str(CERTIFICATE),
    pri_key_filepath=str(PRIVATE_KEY),
    ca_filepath=str(ROOT_CA),
    client_id=CLIENT_ID,
    clean_session=True,
    keep_alive_secs=30
)


print("\nConnecting to AWS IoT Core...")

connect_future = mqtt_connection.connect()
connect_future.result()

print("Connected successfully!")


# --------------------------------------------------
# Publish JSON
# --------------------------------------------------

payload = json.dumps(event)

print("\nPublishing event...")
print(f"Topic: {TOPIC}")

mqtt_connection.publish(
    topic=TOPIC,
    payload=payload,
    qos=mqtt.QoS.AT_LEAST_ONCE
)

print("\nJSON published successfully:")
print(json.dumps(event, indent=2))


# --------------------------------------------------
# Wait for publish
# --------------------------------------------------

time.sleep(2)


# --------------------------------------------------
# Disconnect
# --------------------------------------------------

mqtt_connection.disconnect().result()

print("\nDisconnected from AWS IoT Core.")