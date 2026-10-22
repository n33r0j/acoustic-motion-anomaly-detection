from awscrt import mqtt
from awsiot import mqtt_connection_builder
import json
from pathlib import Path

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


def connect_mqtt():

    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=ENDPOINT,
        cert_filepath=str(CERTIFICATE),
        pri_key_filepath=str(PRIVATE_KEY),
        ca_filepath=str(ROOT_CA),
        client_id=CLIENT_ID,
        clean_session=False,
        keep_alive_secs=30
    )

    print("Connecting to AWS IoT Core...")

    mqtt_connection.connect().result()

    print("Connected to AWS IoT Core")

    return mqtt_connection


def publish_event(mqtt_connection, event):

    payload = json.dumps(event)

    print("Publishing event...")
    print(payload)

    mqtt_connection.publish(
        topic=TOPIC,
        payload=payload,
        qos=mqtt.QoS.AT_LEAST_ONCE
    )

    print("Event published successfully")