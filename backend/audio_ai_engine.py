import streamlit as st
import json
import os
import numpy as np
import librosa

#Page UI settings
st.set_page_config(
    page_title="DASHBOARD",
    page_icon="🌿",
    layout="centered"
)

#detection engine
def classify_environmental_sounds(audio_path=None):
    print(f"[*] Initializing Sound-Distinction AI Engine...")

    #wieghts
    detected_sounds = {
        "bird_chirps": 0.0,
        "wind_rustle": 0.0,
        "human_speech": 0.0,
        "traffic_hum": 0.0,
        "chainsaw_machinery": 0.0
    }
    
    try:
        if audio_path and os.path.exists(audio_path):
            print(f"[*] Analyzing sound classes for: {audio_path}")
            y, sr = librosa.load(audio_path, sr=22050, duration=10.0)
            
            # 1. Measure Frequency Brightness (Spectral Centroid)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            mean_centroid = np.mean(spectral_centroids)
            
            # 2. Measure Noisiness (Zero Crossing Rate)
            zcr = np.mean(librosa.feature.zero_crossing_rate(y)[0])
            
            print(f"[*] Debug - Mean Centroid: {mean_centroid:.2f} Hz | ZCR: {zcr:.4f}")
            
            # Smart Classification Rule based on acoustic properties:
            if mean_centroid > 3000:
                # High frequency sounds = Birds / Wildlife
                detected_sounds["bird_chirps"] = 0.90
                detected_sounds["wind_rustle"] = 0.10
            elif mean_centroid > 1800:
                # Mid frequency sounds = Wind / Speech / Light ambient
                detected_sounds["wind_rustle"] = 0.60
                detected_sounds["human_speech"] = 0.40
            else:
                # Low frequency heavy rumbles = Traffic or Machinery
                if zcr > 0.1:
                    detected_sounds["chainsaw_machinery"] = 0.75
                    detected_sounds["traffic_hum"] = 0.25
                else:
                    detected_sounds["traffic_hum"] = 0.80
                    detected_sounds["chainsaw_machinery"] = 0.20
        else:
            # Default simulation profile (Bird Chirps)
            print("[*] Using default sample classification profile...")
            detected_sounds["bird_chirps"] = 0.95
            detected_sounds["wind_rustle"] = 0.05

        # Calculate Eco-Health Score based on distinguished sounds
        health_score = (
            (detected_sounds["bird_chirps"] * 95) +
            (detected_sounds["wind_rustle"] * 80) -
            (detected_sounds["traffic_hum"] * 40) -
            (detected_sounds["chainsaw_machinery"] * 90)
        )
        health_score = max(5.0, min(100.0, health_score + 10)) 

        analysis_report = {
            "eco_health_score": round(float(health_score), 2),
            "dominant_sound_classes": detected_sounds,
            "ai_diagnosis": evaluate_health_band(health_score, detected_sounds)
        }
        
        return analysis_report

    except Exception as e:
        print(f"[!] Error in sound classification: {e}")
        return {"error": str(e), "eco_health_score": 50.0}

def evaluate_health_band(score, sounds):
    dominant_sound = max(sounds, key=sounds.get)
    formatted_name = dominant_sound.replace('_', ' ').title()
    
    if score >= 75:
        return {
            "band": "Green (Thriving)",
            "primary_trigger": formatted_name,
            "description": f"Pristine ecosystem. Dominant acoustic signature recognized: '{formatted_name}'."
        }
    elif score >= 40:
        return {
            "band": "Yellow (Moderate Stress)",
            "primary_trigger": formatted_name,
            "description": f"Mixed acoustic environment. Detected activity: '{formatted_name}'."
        }
    else:
        return {
            "band": "Red (Critical Hazard)",
            "primary_trigger": formatted_name,
            "description": f"CRITICAL HAZARD ALERT: Harmful anomaly detected ('{formatted_name}')!"
        }


# --- STREAMLIT USER INTERFACE ---

st.title("🌿 Eco-Health & Sound Distinction Dashboard")
st.markdown("### Translating environmental soundscapes into instant ecological insights.")
st.markdown("---")

# Sidebar Control Panel
st.sidebar.header("🎛️ Control Panel")
input_mode = st.sidebar.radio("Select Input Mode", ["Demo Simulation", "Upload Sound File"])

audio_file_path = None
if input_mode == "Upload Sound File":
    uploaded_file = st.sidebar.file_uploader("Upload Audio (.wav or .mp3)", type=["wav", "mp3"])
    if uploaded_file is not None:
        temp_path = "temp_audio.wav"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        audio_file_path = temp_path
        st.sidebar.success("File uploaded successfully!")

# Run Button
if st.sidebar.button("Run Sound Distinction Analysis", type="primary"):
    with st.spinner("Distinguishing environmental sounds and calculating score..."):
        st.session_state['result'] = classify_environmental_sounds(audio_file_path)
else:
    if 'result' not in st.session_state:
        st.session_state['result'] = classify_environmental_sounds(None)

# Extract Data from Result
current_data = st.session_state['result']
score = current_data["eco_health_score"]
diagnosis = current_data["ai_diagnosis"]
sound_classes = current_data["dominant_sound_classes"]

# --- DASHBOARD DISPLAY COLUMNS ---

col1, col2 = st.columns([1, 1])

with col1:
    st.metric(label="Eco-Health Index Score", value=f"{score} / 100")

with col2:
    band_name = diagnosis["band"]
    if "Green" in band_name:
        st.success(f"Status: {band_name}")
    elif "Yellow" in band_name:
        st.warning(f"Status: {band_name}")
    else:
        st.error(f"Status: {band_name}")

# Visual Meter / Progress Bar
st.markdown("### 📊 Ecosystem Health Meter")
st.progress(score / 100.0)
st.caption(diagnosis["description"])

#SOUND DISTINCTION BREAKDOWN SECTION
st.markdown("---")
st.subheader("🔍 AI Sound Classification Breakdown")
st.write("The AI distinguishes individual sound categories to determine overall habitat health:")

# Display sound classes cleanly using columns and small progress indicators
for sound_name, probability in sound_classes.items():
    display_label = sound_name.replace('_', ' ').title()
    col_a, col_b = st.columns([2, 3])
    with col_a:
        st.text(display_label)
    with col_b:
        st.progress(float(probability))

#RAW JSON INSPECTOR FOR JUDGES
st.markdown("---")
with st.expander("🛠️ View Full Backend JSON Payload"):
    st.json(current_data)