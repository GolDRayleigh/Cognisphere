"""
CropShield AI - mobile app shell with a bottom menu.

Run:      streamlit run main.py
Install:  pip install streamlit numpy
          pip install librosa                # optional: analyse uploaded sound files
          pip install streamlit-geolocation  # optional: exact browser GPS
Theme:    .streamlit/config.toml (purple theme, hides the Deploy button)
"""
import streamlit as st

import ui_kit as ui
from audio_ai_engine import classify_upload
from detectionMapping import get_soil_profile, ip_geolocate
from irrigationPipeline import FLOOD_BASELINE, analyze_irrigation

try:
    from streamlit_geolocation import streamlit_geolocation
except ImportError:
    streamlit_geolocation = None

st.set_page_config(page_title="CropShield", page_icon="🌾", layout="centered",
                   initial_sidebar_state="collapsed")
ui.inject_css()

PLACES = {
    "Lucknow, UP": (26.8393, 80.9231),
    "Jaisalmer, Rajasthan": (26.9157, 70.9083),
    "Nagpur, Maharashtra": (21.1458, 79.0882),
    "Coimbatore, Tamil Nadu": (11.0168, 76.9558),
    "Mangaluru, Karnataka": (12.9141, 74.8560),
    "Srinagar, J&K": (34.0837, 74.7973),
}
# Defaults for every input. Re-assigning each run also keeps values alive while another page is open.
DEFAULTS = {"loc_mode": "Demo Location", "place": "Lucknow, UP", "lat_in": 26.8393,
            "lon_in": 80.9231, "crop": "All typical crops", "water": "Moderate",
            "sound_mode": "Demo Simulation"}
for _k, _v in DEFAULTS.items():
    st.session_state[_k] = st.session_state.get(_k, _v)


# ------------------------------------------------------------------ actions
def current_location():
    mode = st.session_state["loc_mode"]
    if mode == "Demo Location":
        return (*PLACES[st.session_state["place"]], st.session_state["place"])
    if mode == "Enter Coordinates":
        return st.session_state["lat_in"], st.session_state["lon_in"], "Manual coordinates"
    return st.session_state.get("detected") or (*PLACES["Lucknow, UP"], "Not detected yet (Lucknow demo)")


def run_dashboard():
    lat, lon, source = current_location()
    crop = st.session_state["crop"]
    st.session_state["analysis"] = {
        "irr": analyze_irrigation(lat, lon, None if crop.startswith("All") else crop, st.session_state["water"]),
        "source": source, "lat": lat, "lon": lon}


def run_sound():
    up = st.session_state.get("upload") if st.session_state["sound_mode"] == "Upload Sound File" else None
    st.session_state["eco"] = classify_upload(up)


# ------------------------------------------------------------------ bottom menu
PAGES = {"dashboard": "🏠\nDashboard", "chat": "💬\nChatbot",
         "disease": "🍃\nCrop Scan", "sound": "🔊\nEcosystem"}
page = st.radio("Menu", list(PAGES), format_func=PAGES.get, key="bottom_nav",
                horizontal=True, label_visibility="collapsed")


# ------------------------------------------------------------------ dashboard
def auto_detect():
    if streamlit_geolocation:
        st.caption("Tap the button below, then allow location access in your browser.")
        gps = streamlit_geolocation()
        if gps and gps.get("latitude") is not None:
            st.session_state["detected"] = (gps["latitude"], gps["longitude"], "Browser GPS")
    else:
        st.info("For exact GPS: pip install streamlit-geolocation")
    if st.button("📍 Use approximate location (IP)"):
        found = ip_geolocate()
        if found:
            st.session_state["detected"] = found
        else:
            st.error("Could not detect location. Use Demo or Coordinates mode.")
    det = st.session_state.get("detected")
    if det:
        st.success(f"{det[2]}: {det[0]:.4f}, {det[1]:.4f}")
    else:
        st.warning("Location not detected yet. Showing Lucknow demo.")


def field_settings():
    with st.expander("⚙️ Field settings"):
        st.selectbox("Location mode", ["Demo Location", "Enter Coordinates", "Auto-Detect Location"],
                     key="loc_mode")
        mode = st.session_state["loc_mode"]
        if mode == "Demo Location":
            st.selectbox("Choose a place", list(PLACES), key="place")
        elif mode == "Enter Coordinates":
            c1, c2 = st.columns(2)
            c1.number_input("Latitude", format="%.4f", key="lat_in")
            c2.number_input("Longitude", format="%.4f", key="lon_in")
        else:
            auto_detect()

        profile = get_soil_profile(*current_location()[:2])
        if profile is None:
            st.error("These coordinates are outside India.")
        crops = ["All typical crops"] + (profile["typical_crops"] if profile else [])
        if st.session_state["crop"] not in crops:
            st.session_state["crop"] = crops[0]
        st.selectbox("Crop", crops, key="crop")
        st.select_slider("Water availability", ["Low", "Moderate", "High"], key="water")
        st.button("Analyse my field", type="primary", on_click=run_dashboard)


def dashboard():
    if "analysis" not in st.session_state:
        run_dashboard()
    A = st.session_state["analysis"]
    irr = A["irr"]
    ok = "error" not in irr

    body = f'<div class="loc">📍 {ui.esc(A["source"])}'
    if ok:
        body += f' · {ui.esc(irr["result"]["region"])}</div>'
        body += (f'<div><span class="big">{irr["score"]:g}</span><span class="of">/ 100 water efficiency</span></div>'
                 + ui.meter(irr["score"]) + ui.pill(irr["band"]))
    else:
        body += "</div>"
    ui.hero("CropShield AI", "Your field today", body)

    field_settings()
    if not ok:
        ui.card(f'<div class="head">⚠️ {ui.esc(irr["error"])}</div>'
                '<p class="muted">Pick a location in India under Field settings.</p>', warn=True)
        return

    res, prof, focus = irr["result"], irr["profile"], irr["focus"]
    ui.card(f'<div class="muted">Best way to water {ui.esc(irr["focus_crop"])}</div>'
            f'<div class="method">{ui.esc(focus["method"])}</div>'
            f'<div class="chips"><span class="chip">Efficiency {ui.esc(focus["efficiency"])}</span>'
            f'<span class="chip">Saves ~{irr["water_saved_pct"]}% water vs flood</span></div>'
            f'<p>{ui.esc(focus["rationale"])}</p>')
    if irr["water"] == "Low" and "Drip" not in focus["method"]:
        ui.card("💧 Water is limited. Drip irrigation uses the least water, so consider it if you can.", warn=True)

    with st.expander("How is the score calculated?"):
        st.dataframe(irr["rows"], hide_index=True)
        st.caption(f"Heuristic score, not a measurement. Assumes flood irrigation is about {FLOOD_BASELINE:.0f}% efficient.")

    ui.card('<div class="head">🌱 Your soil</div>'
            f'<div class="muted">{ui.esc(res["soil_detected"])} · {ui.esc(prof["texture"])}</div>'
            + ui.facts([("Soil", res["soil_category_used"]), ("pH", prof["pH"]),
                        ("Fertility", prof["fertility"].split(" (")[0]),
                        ("Organic C", f"{prof['organic_carbon_g_kg']} g/kg")]))

    ui.card('<div class="head">🌾 Crops in this region</div>'
            + ui.rows([(c, a["method"].split(" (")[0], f'Efficiency {a["efficiency"]}')
                       for c, a in res["irrigation_advice"].items()]))
    st.caption("General guidance from regional averages, not a soil test. "
               "Check with your nearest Krishi Vigyan Kendra (KVK).")


# ------------------------------------------------------------------ sound ecosystem
def sound():
    if "eco" not in st.session_state:
        run_sound()
    eco = st.session_state["eco"]
    diag = eco["ai_diagnosis"]
    ui.hero("Eco-Health", "Sound Ecosystem",
            f'<div><span class="big">{eco["eco_health_score"]:g}</span><span class="of">/ 100 eco-health</span></div>'
            + ui.meter(eco["eco_health_score"]) + ui.pill(diag["band"]))

    with st.expander("🎧 Sound input"):
        st.selectbox("Input mode", ["Demo Simulation", "Upload Sound File"], key="sound_mode")
        if st.session_state["sound_mode"] == "Upload Sound File":
            st.file_uploader("Upload audio (.wav or .mp3)", type=["wav", "mp3"], key="upload")
        st.button("Analyse soundscape", type="primary", on_click=run_sound)

    ui.card(f'<div class="head">Diagnosis</div><p>{ui.esc(diag["description"])}</p>', warn="error" in eco)
    bars = "".join(f'<div class="srow"><span>{ui.esc(n.replace("_", " ").title())}</span>'
                   f'<div class="bar"><span style="width:{p * 100:.0f}%"></span></div><em>{p * 100:.0f}%</em></div>'
                   for n, p in eco["dominant_sound_classes"].items())
    ui.card('<div class="head">🔍 Sound classification</div>'
            '<div class="muted">How much of each sound type the AI heard</div>' + bars)
    with st.expander("🛠️ Raw JSON payload"):
        st.json(eco)


# ------------------------------------------------------------------ blank placeholders
def placeholder(sub, title):
    ui.hero(sub, title)
    ui.coming_soon()


{"dashboard": dashboard,
 "chat": lambda: placeholder("Ask anything", "Chatbot"),
 "disease": lambda: placeholder("Scan a leaf", "Crop Disease Detection"),
 "sound": sound}[page]()
