"""Sound-distinction engine. Pure logic: no Streamlit code, safe to import."""
import os
import tempfile

import numpy as np

try:
    import librosa
except ImportError:          # only needed for uploaded files; demo mode works without it
    librosa = None


def evaluate_health_band(score, sounds):
    dominant = max(sounds, key=sounds.get)
    name = dominant.replace("_", " ").title()
    if score >= 75:
        return {"band": "Green (Thriving)", "primary_trigger": name,
                "description": f"Pristine ecosystem. Dominant acoustic signature recognized: '{name}'."}
    if score >= 40:
        return {"band": "Yellow (Moderate Stress)", "primary_trigger": name,
                "description": f"Mixed acoustic environment. Detected activity: '{name}'."}
    return {"band": "Red (Critical Hazard)", "primary_trigger": name,
            "description": f"CRITICAL HAZARD ALERT: Harmful anomaly detected ('{name}')!"}


def classify_environmental_sounds(audio_path=None):
    sounds = {"bird_chirps": 0.0, "wind_rustle": 0.0, "human_speech": 0.0,
              "traffic_hum": 0.0, "chainsaw_machinery": 0.0}
    try:
        if audio_path and os.path.exists(audio_path):
            if librosa is None:
                raise RuntimeError("librosa is not installed (pip install librosa).")
            y, sr = librosa.load(audio_path, sr=22050, duration=10.0)
            centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)[0]))  # brightness
            zcr = float(np.mean(librosa.feature.zero_crossing_rate(y)[0]))               # noisiness

            if centroid > 3000:        # high frequency: birds / wildlife
                sounds["bird_chirps"], sounds["wind_rustle"] = 0.90, 0.10
            elif centroid > 1800:      # mid frequency: wind / speech
                sounds["wind_rustle"], sounds["human_speech"] = 0.60, 0.40
            elif zcr > 0.1:            # low + noisy: machinery
                sounds["chainsaw_machinery"], sounds["traffic_hum"] = 0.75, 0.25
            else:                      # low + smooth: traffic
                sounds["traffic_hum"], sounds["chainsaw_machinery"] = 0.80, 0.20
        else:                          # demo profile
            sounds["bird_chirps"], sounds["wind_rustle"] = 0.95, 0.05

        raw = (sounds["bird_chirps"] * 95 + sounds["wind_rustle"] * 80
               - sounds["traffic_hum"] * 40 - sounds["chainsaw_machinery"] * 90)
        score = round(max(5.0, min(100.0, raw + 10)), 2)
        return {"eco_health_score": score, "dominant_sound_classes": sounds,
                "ai_diagnosis": evaluate_health_band(score, sounds)}

    except Exception as e:
        return {"error": str(e), "eco_health_score": 50.0, "dominant_sound_classes": sounds,
                "ai_diagnosis": {"band": "Yellow (Moderate Stress)", "primary_trigger": "Unknown",
                                 "description": f"Sound analysis failed: {e}"}}


def classify_upload(uploaded_file=None):
    """Classify a Streamlit UploadedFile (or run the demo profile when None)."""
    if uploaded_file is None:
        return classify_environmental_sounds(None)
    suffix = os.path.splitext(uploaded_file.name)[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
        f.write(uploaded_file.getbuffer())
        path = f.name
    try:
        return classify_environmental_sounds(path)
    finally:
        os.remove(path)


if __name__ == "__main__":
    print(classify_environmental_sounds(None))
