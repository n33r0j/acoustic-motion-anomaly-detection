import socket
import struct
import wave
import zlib
import os
from datetime import datetime


# --------------------------------------------------
# Configuration
# --------------------------------------------------

HOST = "0.0.0.0"
PORT = 5001

OUTPUT_DIR = "received_events"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# --------------------------------------------------
# Protocol
# --------------------------------------------------

PACKET_MAGIC = 0x414D4144
PROTOCOL_VERSION = 1

HEADER_FORMAT = "<IBBHIIIII"

HEADER_SIZE = struct.calcsize(
    HEADER_FORMAT
)

ACK_FORMAT = "<II"

ACK_SIZE = struct.calcsize(
    ACK_FORMAT
)


# --------------------------------------------------
# Receive exactly N bytes
# --------------------------------------------------

def recv_exact(
    connection,
    size
):
    data = bytearray()

    while len(data) < size:

        chunk = connection.recv(
            size - len(data)
        )

        if not chunk:
            raise ConnectionError(
                "Connection closed while receiving data"
            )

        data.extend(chunk)

    return bytes(data)


# --------------------------------------------------
# Save WAV
# --------------------------------------------------

def save_wav(
    samples,
    filename,
    sample_rate
):
    with wave.open(
        filename,
        "wb"
    ) as wav:

        wav.setnchannels(1)

        wav.setsampwidth(2)

        wav.setframerate(
            sample_rate
        )

        wav.writeframes(
            samples
        )


# --------------------------------------------------
# Handle event
# --------------------------------------------------

def receive_event(
    connection,
    client_address,
    received_sequences
):

    # ----------------------------------------------
    # Header
    # ----------------------------------------------

    header_data = recv_exact(
        connection,
        HEADER_SIZE
    )


    (
        magic,
        version,
        motion,
        reserved,
        sequence,
        timestamp_ms,
        sample_rate,
        sample_count,
        payload_bytes,
        expected_crc
    ) = struct.unpack(
        HEADER_FORMAT,
        header_data
    )


    # ----------------------------------------------
    # Validate header
    # ----------------------------------------------

    if magic != PACKET_MAGIC:
        raise ValueError(
            "Invalid packet magic"
        )


    if version != PROTOCOL_VERSION:
        raise ValueError(
            f"Unsupported protocol version: {version}"
        )


    expected_payload_bytes = (
        sample_count * 2
    )


    if payload_bytes != expected_payload_bytes:
        raise ValueError(
            "Payload size does not match sample count"
        )


    # ----------------------------------------------
    # Receive audio
    # ----------------------------------------------

    audio_data = recv_exact(
        connection,
        payload_bytes
    )


    # ----------------------------------------------
    # CRC verification
    # ----------------------------------------------

    actual_crc = zlib.crc32(
        audio_data
    ) & 0xFFFFFFFF


    if actual_crc != expected_crc:

        print(
            f"CRC ERROR: "
            f"expected={expected_crc:#010x}, "
            f"actual={actual_crc:#010x}"
        )

        raise ValueError(
            "Audio CRC verification failed"
        )


    # ----------------------------------------------
    # Duplicate detection
    # ----------------------------------------------

    if sequence in received_sequences:

        print(
            f"DUPLICATE EVENT: {sequence}"
        )

    else:

        received_sequences.add(
            sequence
        )


        # ------------------------------------------
        # Generate filename
        # ------------------------------------------

        now = datetime.now()

        timestamp_string = (
            now.strftime(
                "%Y%m%d_%H%M%S"
            )
        )


        filename = os.path.join(
            OUTPUT_DIR,
            f"event_{sequence}_"
            f"{timestamp_string}.wav"
        )


        # ------------------------------------------
        # Save WAV
        # ------------------------------------------

        save_wav(
            audio_data,
            filename,
            sample_rate
        )


        print()
        print(
            "EVENT RECEIVED"
        )

        print(
            f"Sequence : {sequence}"
        )

        print(
            f"Motion   : {bool(motion)}"
        )

        print(
            f"Samples  : {sample_count}"
        )

        print(
            f"Rate     : {sample_rate} Hz"
        )

        print(
            f"Duration : "
            f"{sample_count / sample_rate:.2f} sec"
        )

        print(
            f"CRC      : OK"
        )

        print(
            f"Saved    : {filename}"
        )


    # ----------------------------------------------
    # Send ACK
    # ----------------------------------------------

    ack = struct.pack(
        ACK_FORMAT,
        PACKET_MAGIC,
        sequence
    )

    connection.sendall(
        ack
    )


# --------------------------------------------------
# Server
# --------------------------------------------------

def main():

    received_sequences = set()


    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )


    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )


    server.bind(
        (HOST, PORT)
    )


    server.listen(5)


    print(
        "=================================="
    )

    print(
        "ESP32 Acoustic Event Receiver"
    )

    print(
        "=================================="
    )

    print(
        f"Listening on TCP port {PORT}"
    )

    print(
        f"Output directory: {OUTPUT_DIR}"
    )

    print()


    while True:

        connection, address = (
            server.accept()
        )


        print(
            f"ESP32 connected: {address}"
        )


        connection.settimeout(
            10
        )


        try:

            while True:

                receive_event(
                    connection,
                    address,
                    received_sequences
                )

        except (
            ConnectionError,
            TimeoutError,
            socket.timeout,
            ValueError
        ) as error:

            print(
                f"Connection ended: {error}"
            )


        finally:

            connection.close()

            print(
                "ESP32 disconnected"
            )

            print()


# --------------------------------------------------
# Entry point
# --------------------------------------------------

if __name__ == "__main__":
    main()