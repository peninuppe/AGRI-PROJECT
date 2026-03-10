"""
Vision utility for soil and land image analysis.
Uses OpenCV for basic image processing and Gemini Vision API for detailed analysis.
"""

import cv2
import numpy as np
import os
import json
import google.genai as genai
from google.genai import types


def analyze_image_opencv(image_path):
    """
    Use OpenCV to extract basic soil color and texture information.
    Returns a dict with color, texture, and moisture indicators.
    """
    img = cv2.imread(image_path)
    if img is None:
        return {"error": "Could not read image"}

    img_resized = cv2.resize(img, (300, 300))

    hsv = cv2.cvtColor(img_resized, cv2.COLOR_BGR2HSV)
    avg_hue = np.mean(hsv[:, :, 0])
    avg_sat = np.mean(hsv[:, :, 1])
    avg_val = np.mean(hsv[:, :, 2])

    b, g, r = cv2.split(img_resized)
    avg_r = np.mean(r)
    avg_g = np.mean(g)
    avg_b = np.mean(b)

    soil_color = classify_soil_color(avg_r, avg_g, avg_b, avg_hue, avg_sat)

    gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    texture = "Coarse" if laplacian_var > 500 else "Medium" if laplacian_var > 150 else "Fine"

    green_ratio = avg_g / (avg_r + avg_g + avg_b + 1e-6)
    vegetation = "High" if green_ratio > 0.38 else "Moderate" if green_ratio > 0.30 else "Low"

    moisture_score = (avg_b / 255.0) * 0.5 + (1 - avg_val / 255.0) * 0.5
    moisture = "High" if moisture_score > 0.45 else "Medium" if moisture_score > 0.30 else "Low"

    return {
        "soil_color": soil_color,
        "texture": texture,
        "vegetation_presence": vegetation,
        "moisture_level": moisture,
        "avg_rgb": {"r": round(avg_r, 1), "g": round(avg_g, 1), "b": round(avg_b, 1)},
        "laplacian_variance": round(laplacian_var, 2)
    }


def classify_soil_color(r, g, b, hue, sat):
    if r > 120 and g < 90 and b < 90:
        return "Red Loamy Soil"
    elif r > 140 and g > 110 and b < 100:
        return "Brown Sandy Soil"
    elif r < 80 and g < 80 and b < 80:
        return "Black Cotton Soil"
    elif r > 160 and g > 150 and b > 130:
        return "Alluvial Soil"
    elif r > 170 and g > 160 and b > 140:
        return "Sandy Loam Soil"
    elif 80 <= r <= 140 and 70 <= g <= 120 and b < 100:
        return "Red Sandy Soil"
    elif g > r and g > b:
        return "Loamy Soil with Vegetation"
    else:
        return "Mixed Soil"


def analyze_image_with_gemini(image_path, api_key):
    """
    Use Gemini Vision API (google-genai SDK) to perform comprehensive soil analysis.
    """
    # Handle missing or empty API key
    if not api_key or api_key == "":
        return {
            "soil_type": "Mixed Agricultural Soil",
            "soil_color": "Brown",
            "texture": "Medium",
            "moisture_level": "Medium",
            "vegetation_presence": "Moderate",
            "ph_estimate": "Neutral",
            "drainage": "Moderate",
            "organic_matter": "Medium",
            "land_suitability": "Suitable for general crop cultivation",
            "detected_issues": "None",
            "confidence": "Low",
            "note": "API key not configured. Used fallback values."
        }
    
    try:
        client = genai.Client(api_key=api_key)

        ext = os.path.splitext(image_path)[1].lower()
        mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                    ".png": "image/png", ".webp": "image/webp", ".bmp": "image/bmp"}
        mime_type = mime_map.get(ext, "image/jpeg")

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        prompt = """Analyze this land/soil image and provide a detailed agricultural assessment. 
Return your response ONLY as a valid JSON object with these exact keys:
{
  "soil_type": "name of soil type (e.g., Red Loamy Soil, Black Cotton Soil, Alluvial Soil, Sandy Loam Soil)",
  "soil_color": "observed color",
  "texture": "Fine / Medium / Coarse",
  "moisture_level": "Low / Medium / High",
  "vegetation_presence": "Low / Moderate / High",
  "ph_estimate": "Acidic / Neutral / Alkaline",
  "drainage": "Poor / Moderate / Good",
  "organic_matter": "Low / Medium / High",
  "land_suitability": "one sentence about what the land is suitable for",
  "detected_issues": "any visible issues or None",
  "confidence": "Low / Medium / High"
}
Return ONLY the JSON, no other text."""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt
            ]
        )

        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        return json.loads(text)

    except json.JSONDecodeError:
        return {
            "soil_type": "Mixed Agricultural Soil",
            "soil_color": "Brown",
            "texture": "Medium",
            "moisture_level": "Medium",
            "vegetation_presence": "Moderate",
            "ph_estimate": "Neutral",
            "drainage": "Moderate",
            "organic_matter": "Medium",
            "land_suitability": "Suitable for general crop cultivation",
            "detected_issues": "None",
            "confidence": "Low",
            "note": "Used fallback values due to JSON parse error."
        }
    except Exception as e:
        return {"error": str(e), "soil_type": "Unknown"}


def full_image_analysis(image_path, api_key):
    """Combine OpenCV and Gemini analysis."""
    opencv_data = analyze_image_opencv(image_path)
    gemini_data = analyze_image_with_gemini(image_path, api_key)
    combined = {**opencv_data, **gemini_data}
    if "error" in gemini_data or gemini_data.get("soil_type") == "Unknown":
        combined["soil_type"] = opencv_data.get("soil_color", "Mixed Soil")
    return combined
