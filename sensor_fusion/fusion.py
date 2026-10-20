def sensor_fusion(acoustic_event, acoustic_confidence, motion):

    CONFIDENCE_THRESHOLD = 0.46

    if (
        acoustic_confidence > CONFIDENCE_THRESHOLD
        and motion == 1
        and acoustic_event in ["footsteps", "glass_break"]
    ):
        result = "possible_intrusion"
        severity = "high"

    elif acoustic_event == "normal" and acoustic_confidence > CONFIDENCE_THRESHOLD:
        result = "normal"
        severity = "low"

    elif acoustic_event == "knocking" and acoustic_confidence > CONFIDENCE_THRESHOLD:
        result = "activity_detected"
        severity = "medium"

    elif acoustic_confidence <= CONFIDENCE_THRESHOLD:
        result = "uncertain"
        severity = "low"

    else:
        result = "acoustic_event"
        severity = "medium"

    return {
        "acoustic_event": acoustic_event,
        "confidence": acoustic_confidence,
        "motion": motion,
        "result": result,
        "severity": severity
    }
if __name__ == "__main__":
    print(sensor_fusion("footsteps", 0.80, 0))