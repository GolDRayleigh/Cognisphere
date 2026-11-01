import json
import re

from irrigationAdvisor import recommend_irrigation_method
from detectionMapping import get_precise_india_soil_profile, get_soil_profile


# ---------- 1. Translate soil output -> labels the irrigation function knows ----------
def map_soil_category(soil_profile: dict) -> str:
    taxonomy = soil_profile.get("taxonomy", "").lower()
    texture = soil_profile.get("texture", "").lower()

    if "desert" in taxonomy or "aridisol" in taxonomy:
        return "Arid / Desert Soil"
    if "vertisol" in taxonomy or "black" in taxonomy:
        return "Black Soil (Regur)"
    if "laterite" in taxonomy or "red and yellow" in taxonomy:
        return "Red and Laterite Soil"
    if "alluvial" in taxonomy:
        return "Alluvial Soil"
    if texture.startswith("sandy"):
        return "Sandy Soil"
    return "Other Soil"


# ---------- 2. Translate crop names -> labels the irrigation function knows ----------
CROP_ALIASES = {
    "Bajra (Pearl Millet)": "Millets",
    "Jowar": "Millets",
    "Sorghum": "Millets",
    "Ragi": "Millets",
    "Millets": "Millets",
    "Paddy": "Rice",
    "Chickpea": "Pulses",
    "Guar": "Pulses",
    "Potato": "Vegetables",
    "Citrus": "Orchard Crops",
    "Apples": "Orchard Crops",
    "Pears": "Orchard Crops",
    "Cashew": "Orchard Crops",
    "Coconut": "Orchard Crops",
}

def normalize_crop(crop: str) -> str:
    return CROP_ALIASES.get(crop, crop)  # unchanged if no alias needed


# ---------- 3. The pipeline ----------
def get_irrigation_for_location(lat, lon, crop_name=None, water_availability="Moderate"):
    soil_json = json.loads(get_precise_india_soil_profile(lat, lon))

    if "error" in soil_json:
        return soil_json

    profile = soil_json["soil_profile"]
    soil_category = map_soil_category(profile)

    # If no crop given, advise for every typical crop of that region
    crops = [crop_name] if crop_name else profile.get("typical_crops", [])

    advice = {}
    for crop in crops:
        advice[crop] = recommend_irrigation_method(
            soil_category, normalize_crop(crop), water_availability
        )

    return {
        "location": soil_json["location"],
        "region": profile["region"],
        "soil_detected": profile["taxonomy"],
        "soil_category_used": soil_category,
        "irrigation_advice": advice,
    }


# ---------- 4. Water-efficiency meter ----------
# Heuristic adjustments in percentage points. Tune with real agronomic data.
SOIL_ADJ = {
    "Black Soil (Regur)": +3,      # holds moisture well
    "Alluvial Soil": +2,
    "Red and Laterite Soil": 0,
    "Other Soil": 0,
    "Sandy Soil": -4,              # drains fast
    "Arid / Desert Soil": -4,      # drains fast + high evaporation
}
FLOOD_BASELINE = 40.0              # assumed efficiency of flood irrigation (%)


def range_mid(text: str) -> float:
    """'90% - 95%' -> 92.5"""
    nums = [float(n) for n in re.findall(r"\d+", text)]
    return sum(nums) / len(nums) if nums else 0.0


def water_efficiency(eff_range, soil_cat, method, water):
    """Return (score 0-100, band, breakdown rows)."""
    is_drip = "Drip" in method
    base = range_mid(eff_range)
    soil_adj = SOIL_ADJ.get(soil_cat, 0) * (0.5 if is_drip else 1)   # drip works at the root zone
    water_adj = -5 if (water == "Low" and not is_drip) else 0        # scarcity makes losses costly
    score = round(max(0.0, min(100.0, base + soil_adj + water_adj)), 1)
    band = ("Green (Water-Smart)" if score >= 85
            else "Yellow (Fair, can be improved)" if score >= 65
            else "Red (Water-Wasteful)")
    rows = [{"Factor": "Method baseline", "Points": round(base, 1)},
            {"Factor": f"Soil effect ({soil_cat})", "Points": round(soil_adj, 1)},
            {"Factor": f"Water availability ({water})", "Points": water_adj},
            {"Factor": "Final score", "Points": score}]
    return score, band, rows


def analyze_irrigation(lat, lon, crop_name=None, water="Moderate"):
    """Everything the dashboard needs for the irrigation side, in one call."""
    result = get_irrigation_for_location(lat, lon, crop_name, water)
    if "error" in result:
        return result
    crop, focus = next(iter(result["irrigation_advice"].items()))
    score, band, rows = water_efficiency(focus["efficiency"], result["soil_category_used"],
                                         focus["method"], water)
    return {"result": result, "profile": get_soil_profile(lat, lon), "focus_crop": crop,
            "focus": focus, "score": score, "band": band, "rows": rows, "water": water,
            "water_saved_pct": round(max(0.0, (1 - FLOOD_BASELINE / score) * 100)) if score else 0}


if __name__ == "__main__":
    # Lucknow, wheat
    print(json.dumps(get_irrigation_for_location(26.8393, 80.9231, "Wheat"), indent=4))

    # Lucknow, all typical crops of the region
    print(json.dumps(get_irrigation_for_location(26.8393, 80.9231), indent=4))