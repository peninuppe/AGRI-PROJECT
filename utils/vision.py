"""
Vision utility for soil and land image analysis.
Uses Gemini Vision API for comprehensive analysis.
Note: OpenCV removed due to Vercel size limitations.
"""

import os
import json
import google.genai as genai
from google.genai import types


def analyze_image_opencv(image_path):
    """
    Fallback function when OpenCV is not available.
    Returns basic fallback values.
    """
    return {
        "soil_color": "Brown",
        "texture": "Medium",
        "vegetation_presence": "Moderate",
        "moisture_level": "Medium",
        "avg_rgb": {"r": 120, "g": 100, "b": 80},
        "laplacian_variance": 200,
        "note": "Using Gemini-only analysis (OpenCV disabled for deployment)"
    }


def classify_soil_color(r, g, b, hue, sat):
    """Fallback soil color classification."""
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


def analyze_image_with_gemini(image_path, api_key, image_bytes=None):
    """
    Use Gemini Vision API (google-genai SDK) to perform comprehensive soil analysis.
    
    Args:
        image_path: Path to image file (used for extension detection)
        api_key: Gemini API key
        image_bytes: Image bytes (optional - for Vercel/in-memory processing)
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

        # Get extension from path or use jpeg as default
        if image_path:
            ext = os.path.splitext(image_path)[1].lower()
        else:
            ext = ".jpg"
        mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                    ".png": "image/png", ".webp": "image/webp", ".bmp": "image/bmp"}
        mime_type = mime_map.get(ext, "image/jpeg")

        # Use provided bytes or read from file
        if image_bytes is not None:
            image_data = image_bytes
        else:
            with open(image_path, "rb") as f:
                image_data = f.read()

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
                types.Part.from_bytes(data=image_data, mime_type=mime_type),
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


def full_image_analysis(image_path, api_key, image_bytes=None):
    """Use Gemini for image analysis (OpenCV disabled for Vercel).
    
    Args:
        image_path: Path to image file (for extension detection)
        api_key: Gemini API key
        image_bytes: Image bytes (optional - for Vercel/in-memory processing)
    """
    # Skip OpenCV analysis - use Gemini only
    gemini_data = analyze_image_with_gemini(image_path, api_key, image_bytes)
    
    # Use Gemini data as the primary source
    if "error" in gemini_data or gemini_data.get("soil_type") == "Unknown":
        # Return fallback values
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
            "confidence": "Low"
        }
    
    return gemini_data
