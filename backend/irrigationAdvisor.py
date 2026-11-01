def recommend_irrigation_method(soil_type, crop_name, water_availability="Moderate"):
    """
    Recommends the best modern irrigation method based on soil type, 
    crop category, and regional water constraints.
    """
    recommendations = {
        "method": "",
        "efficiency": "",
        "rationale": "",
        "key_benefit": "Water conservation and targeted nutrient delivery."
    }
    
    # Logic for selecting optimal irrigation method
    if soil_type in ["Sandy Soil", "Arid / Desert Soil"] or crop_name in ["Sugarcane", "Cotton", "Vegetables", "Orchard Crops"]:
        recommendations["method"] = "Drip Irrigation (Micro-Irrigation)"
        recommendations["efficiency"] = "90% - 95%"
        recommendations["rationale"] = (
            "Delivers water drop-by-drop directly to the root zone. "
            "Ideal for sandy or loose soils to prevent deep percolation loss and minimizes weed growth between rows."
        )
    elif soil_type in ["Red and Laterite Soil", "Black Soil (Regur)"] and crop_name in ["Wheat", "Rice", "Millets", "Pulses"]:
        recommendations["method"] = "Sprinkler Irrigation System"
        recommendations["efficiency"] = "75% - 85%"
        recommendations["rationale"] = (
            "Mimics natural rainfall, making it excellent for uneven terrain "
            "and soils where uniform distribution prevents surface crusting and helps maintain soil structure."
        )
    else:
        recommendations["method"] = "Smart Furrow Irrigation with Moisture Sensors"
        recommendations["efficiency"] = "65% - 75%"
        recommendations["rationale"] = (
            "Optimized surface method utilizing targeted channels paired with automated timing "
            "to prevent waterlogging in heavier clay or alluvium profiles."
        )
        
    return recommendations

# --- Example Integration Test ---
if __name__ == "__main__":
    # Simulating data passed from your soil detector
    sample_soil = "Alluvial Soil"
    sample_crop = "Wheat"
    
    print(f"--- CropShield AI Irrigation Advisor ---")
    print(f"Target Soil: {sample_soil} | Target Crop: {sample_crop}\n")
    
    advice = recommend_irrigation_method(sample_soil, sample_crop)
    
    import json
    print(json.dumps(advice, indent=4))