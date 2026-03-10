"""
Gemini AI integration for agricultural advice and multilingual support.
Uses the new google-genai SDK.
"""

import json
import google.genai as genai


SUPPORTED_LANGUAGES = {
    "en": "English",
    "ta": "Tamil",
    "hi": "Hindi",
    "te": "Telugu",
    "kn": "Kannada"
}


def generate_agricultural_advice(soil_data, recommended_crops, profit_data, state, api_key, language="en"):
    """
    Generate professional agricultural advice using Gemini API.
    """
    try:
        client = genai.Client(api_key=api_key)

        top_crop = profit_data[0]["crop"] if profit_data else "the recommended crop"
        top_profit = profit_data[0]["profit"] if profit_data else 0
        crop_names = [c["crop"] for c in recommended_crops[:3]]
        lang_name = SUPPORTED_LANGUAGES.get(language, "English")

        prompt = f"""You are an expert agricultural scientist and farm advisor in India.
        
Soil Analysis Results:
- Soil Type: {soil_data.get('soil_type', 'Unknown')}
- Texture: {soil_data.get('texture', 'Medium')}
- Moisture Level: {soil_data.get('moisture_level', 'Medium')}
- pH Estimate: {soil_data.get('ph_estimate', 'Neutral')}
- Organic Matter: {soil_data.get('organic_matter', 'Medium')}
- Drainage: {soil_data.get('drainage', 'Moderate')}
- Vegetation: {soil_data.get('vegetation_presence', 'Moderate')}
- Land Suitability: {soil_data.get('land_suitability', 'General cultivation')}

Location: {state}, India
Top Recommended Crops: {', '.join(crop_names)}
Most Profitable Crop: {top_crop} (estimated profit ₹{top_profit:,.0f} per acre)

Please provide expert farming advice in {lang_name} language. Return ONLY a valid JSON object:
{{
  "overview": "2-3 sentence overview of the soil and land condition",
  "top_crop_advice": "2-3 sentences explaining why {top_crop} is the best choice",
  "risks": "List 2-3 farming risks and how to mitigate them",
  "irrigation": "Specific irrigation recommendations for {top_crop}",
  "fertilizer": "Fertilizer and nutrient management advice",
  "market_tip": "Market and selling strategy tip for the farmer",
  "best_season": "Best planting season and timing advice"
}}

Respond ONLY with the JSON. Be practical, specific, and farmer-friendly."""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        return json.loads(text)

    except json.JSONDecodeError:
        return _fallback_advice(top_crop if profit_data else "Groundnut", state)
    except Exception as e:
        return {"error": str(e), **_fallback_advice("Groundnut", state)}


def _fallback_advice(top_crop, state):
    return {
        "overview": f"The soil analysis indicates moderate fertility suitable for cultivation in {state}. The land shows potential for multiple crop varieties.",
        "top_crop_advice": f"{top_crop} is recommended based on soil characteristics and regional climate patterns. It offers good profitability with moderate input requirements.",
        "risks": "Monitor for pest infestations during monsoon. Ensure proper drainage to prevent waterlogging. Watch for price fluctuations in the market.",
        "irrigation": "Use drip irrigation or furrow irrigation. Maintain consistent soil moisture, especially during flowering stage.",
        "fertilizer": "Apply balanced NPK fertilizer. Use organic compost to improve soil health. Apply micronutrients like zinc if soil tests indicate deficiency.",
        "market_tip": "Consider joining a Farmer Producer Organization (FPO) for better market access. Explore e-NAM platform for online crop trading.",
        "best_season": "Kharif season (June-October) is ideal for most crops in this region. Plan sowing after the first good rains."
    }


def translate_text(text, target_language, api_key):
    """Translate text to target language using Gemini."""
    if target_language == "en":
        return text

    lang_name = SUPPORTED_LANGUAGES.get(target_language, "English")
    if lang_name == "English":
        return text

    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""Translate the following text to {lang_name}. 
Return ONLY the translated text, nothing else.

Text to translate:
{text}"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text.strip()

    except Exception:
        return text


def get_weather_insights(state, district, api_key):
    """Get AI-generated weather and seasonal insights for a location."""
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""Provide brief agricultural weather insights for {district}, {state}, India.
Return ONLY a JSON object:
{{
  "avg_rainfall_mm": <number>,
  "avg_temp_celsius": <number>,
  "primary_season": "Kharif/Rabi/Annual",
  "climate_type": "brief description",
  "farming_challenges": "brief description"
}}"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())

    except Exception:
        return {
            "avg_rainfall_mm": 90,
            "avg_temp_celsius": 30,
            "primary_season": "Kharif",
            "climate_type": "Semi-arid to sub-humid",
            "farming_challenges": "Irregular rainfall and temperature extremes"
        }
