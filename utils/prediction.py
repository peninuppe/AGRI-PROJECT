"""
Crop recommendation and yield prediction engine.
Uses crop_dataset.csv to match soil and climate data.
"""

import pandas as pd
import os


DATASET_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'crop_dataset.csv')
PRICE_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'price_dataset.csv')

# Climate data by Indian state/district (avg rainfall mm, temp C)
CLIMATE_DATA = {
    "Tamil Nadu": {"rainfall": 95, "temp": 30, "season": "Kharif"},
    "Andhra Pradesh": {"rainfall": 90, "temp": 32, "season": "Kharif"},
    "Telangana": {"rainfall": 85, "temp": 33, "season": "Kharif"},
    "Karnataka": {"rainfall": 110, "temp": 28, "season": "Kharif"},
    "Kerala": {"rainfall": 300, "temp": 27, "season": "Annual"},
    "Maharashtra": {"rainfall": 80, "temp": 30, "season": "Kharif"},
    "Gujarat": {"rainfall": 60, "temp": 33, "season": "Kharif"},
    "Rajasthan": {"rainfall": 35, "temp": 35, "season": "Kharif"},
    "Punjab": {"rainfall": 70, "temp": 25, "season": "Rabi"},
    "Haryana": {"rainfall": 65, "temp": 26, "season": "Rabi"},
    "Uttar Pradesh": {"rainfall": 90, "temp": 28, "season": "Rabi"},
    "Madhya Pradesh": {"rainfall": 100, "temp": 30, "season": "Kharif"},
    "Bihar": {"rainfall": 120, "temp": 28, "season": "Kharif"},
    "West Bengal": {"rainfall": 160, "temp": 27, "season": "Kharif"},
    "Odisha": {"rainfall": 150, "temp": 29, "season": "Kharif"},
    "Chhattisgarh": {"rainfall": 130, "temp": 30, "season": "Kharif"},
    "Jharkhand": {"rainfall": 120, "temp": 28, "season": "Kharif"},
    "Assam": {"rainfall": 200, "temp": 25, "season": "Kharif"},
    "Himachal Pradesh": {"rainfall": 110, "temp": 18, "season": "Rabi"},
    "Uttarakhand": {"rainfall": 130, "temp": 20, "season": "Rabi"},
    "default": {"rainfall": 90, "temp": 30, "season": "Kharif"}
}

SOIL_TYPE_MAP = {
    "Red Loamy Soil": ["Red Loamy", "Red Sandy"],
    "Black Cotton Soil": ["Black Cotton"],
    "Alluvial Soil": ["Alluvial", "Loamy"],
    "Sandy Loam Soil": ["Sandy Loam", "Sandy"],
    "Loamy Soil with Vegetation": ["Loamy", "Alluvial"],
    "Brown Sandy Soil": ["Sandy Loam", "Sandy"],
    "Mixed Soil": ["Loamy", "Clay Loam", "Sandy Loam"],
    "Clay Loam Soil": ["Clay Loam"],
}


def get_climate_data(state, district=None):
    """Fetch climate data for state. Returns dict with rainfall, temp, season."""
    climate = CLIMATE_DATA.get(state, CLIMATE_DATA["default"]).copy()
    return climate


def recommend_crops(soil_type, state, district=None, top_n=5):
    """
    Recommend top N crops based on soil type and climate data.
    Returns list of dicts with crop info and suitability score.
    """
    try:
        df = pd.read_csv(DATASET_PATH)
    except Exception as e:
        return {"error": f"Could not load crop dataset: {e}"}

    climate = get_climate_data(state, district)
    rainfall = climate["rainfall"]
    temp = climate["temp"]

    # Map soil type to dataset soil keywords
    soil_keywords = SOIL_TYPE_MAP.get(soil_type, ["Loamy", "Sandy Loam"])

    results = []
    for _, row in df.iterrows():
        score = 0

        # Soil match
        for keyword in soil_keywords:
            if keyword.lower() in str(row["soil_type"]).lower():
                score += 40
                break

        # Rainfall match
        if row["rainfall_min"] <= rainfall <= row["rainfall_max"]:
            score += 30
        elif abs(rainfall - row["rainfall_min"]) < 20 or abs(rainfall - row["rainfall_max"]) < 20:
            score += 15

        # Temperature match
        if row["temp_min"] <= temp <= row["temp_max"]:
            score += 30
        elif abs(temp - row["temp_min"]) < 5 or abs(temp - row["temp_max"]) < 5:
            score += 15

        if score > 0:
            results.append({
                "crop": row["crop"],
                "soil_type": row["soil_type"],
                "yield_per_acre": row["yield_per_acre"],
                "cost_per_acre": row["cost_per_acre"],
                "season": row["season"],
                "suitability_score": score,
                "rainfall_required": f"{row['rainfall_min']}–{row['rainfall_max']} mm",
                "temp_required": f"{row['temp_min']}–{row['temp_max']}°C"
            })

    # Deduplicate by crop name, keep highest score
    seen = {}
    for item in results:
        name = item["crop"]
        if name not in seen or item["suitability_score"] > seen[name]["suitability_score"]:
            seen[name] = item

    sorted_crops = sorted(seen.values(), key=lambda x: x["suitability_score"], reverse=True)
    return sorted_crops[:top_n]


def get_price_data():
    """Load market price data for all crops."""
    try:
        df = pd.read_csv(PRICE_PATH)
        return {row["crop"]: row["price_per_kg"] for _, row in df.iterrows()}
    except Exception:
        return {
            "Paddy": 22, "Wheat": 21, "Maize": 20, "Groundnut": 65,
            "Cotton": 70, "Sugarcane": 3.5, "Millet": 23, "Sorghum": 30,
            "Soybean": 45, "Turmeric": 150, "Banana": 25, "Tomato": 20,
            "Onion": 18, "Chilli": 120, "Sunflower": 55
        }
