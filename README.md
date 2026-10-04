# Privacy-Preserving Acoustic + Motion Anomaly Detection System

A privacy-preserving environmental anomaly detection system combining acoustic sensing and motion detection.

## Project Overview

The system uses an ESP32 with a microphone and PIR sensor to detect unusual environmental events.

The acoustic signal is processed at the edge using MFCC feature extraction and a machine-learning model. PIR provides motion information. These outputs are combined through sensor fusion to determine whether an environmental anomaly is present.

Processed events are transmitted to the cloud using Wi-Fi and MQTT.

## Architecture

Microphone + PIR
        ↓
      ESP32
        ↓
  Edge Processing
        ↓
 Acoustic ML + Motion Detection
        ↓
    Sensor Fusion
        ↓
     Wi-Fi/MQTT
        ↓
   Cloud Database
        ↓
     Dashboard

## Main Features

- Acoustic event classification
- MFCC feature extraction
- PIR motion detection
- Sensor fusion
- Edge AI processing
- MQTT communication
- Cloud event storage
- Web dashboard
- Privacy-preserving processing

## Team

### Member 1
Audio dataset, MFCC, ML, edge processing and sensor fusion.

### Member 2
ESP32, PIR, Wi-Fi, MQTT, cloud, database and dashboard.

## Technology Stack

- ESP32
- Python
- NumPy
- SciPy / librosa
- Scikit-learn
- MQTT
- Cloud database
- Web dashboard
- Git / GitHub
