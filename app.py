"""
AI-Based Smart Crop Recommendation and Profit Prediction System
Flask Backend Application

Team: Penin, Thirupathi, Mallikarjuna
University: Dhanalakshmi Srinivasan University
"""

import os
import json
import uuid
from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

from utils.vision import full_image_analysis
from utils.prediction import recommend_crops, get_climate_data, get_price_data
from utils.profit_calc import calculate_profit, get_best_crop
from utils.gemini_ai import generate_agricultural_advice, translate_text, get_weather_insights

# ─── App Configuration ───────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))

UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp"}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ─── Gemini API Key ───────────────────────────────────────────────────────────
# API key is loaded from environment variable API_KEY (set in Vercel dashboard)
# NEVER hardcode this key — set it in Vercel Environment Variables as "API_KEY"
GEMINI_API_KEY = os.environ.get("API_KEY", "")
if not GEMINI_API_KEY:
    import warnings
    warnings.warn("API_KEY environment variable is not set. Gemini features will not work.")

# ─── Indian States List ────────────────────────────────────────────────────────
INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman and Nicobar Islands", "Chandigarh", "Delhi", "Jammu and Kashmir",
    "Ladakh", "Lakshadweep", "Puducherry"
]


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Home page with image upload and location form."""
    return render_template("index.html", states=INDIAN_STATES)


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Main analysis endpoint.
    Receives: image file, state, district, acres, language
    Returns: full analysis JSON
    """
    try:
        # ── Validate file ──────────────────────────────────────────────────
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files["image"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type. Use JPG, PNG, or WebP"}), 400

        # ── Save image ─────────────────────────────────────────────────────
        ext = file.filename.rsplit(".", 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
        file.save(save_path)

        # ── Form data ──────────────────────────────────────────────────────
        state = request.form.get("state", "Tamil Nadu")
        district = request.form.get("district", "")
        acres = float(request.form.get("acres", 1))
        language = request.form.get("language", "en")
        # Use server-side API key from environment (never exposed to frontend)
        api_key = GEMINI_API_KEY

        # ── Step 1: Image analysis ─────────────────────────────────────────
        soil_data = full_image_analysis(save_path, api_key)

        # ── Step 2: Climate data ───────────────────────────────────────────
        climate = get_climate_data(state, district)

        # ── Step 3: Crop recommendations ──────────────────────────────────
        soil_type = soil_data.get("soil_type", "Mixed Soil")
        crops = recommend_crops(soil_type, state, district, top_n=6)

        if not crops or isinstance(crops, dict):
            crops = [
                {"crop": "Groundnut", "yield_per_acre": 1200, "cost_per_acre": 25000, "season": "Kharif", "suitability_score": 70, "soil_type": "Red Loamy", "rainfall_required": "50–100 mm", "temp_required": "25–35°C"},
                {"crop": "Maize", "yield_per_acre": 2500, "cost_per_acre": 20000, "season": "Kharif", "suitability_score": 65, "soil_type": "Sandy Loam", "rainfall_required": "50–100 mm", "temp_required": "18–30°C"},
                {"crop": "Cotton", "yield_per_acre": 900, "cost_per_acre": 35000, "season": "Kharif", "suitability_score": 60, "soil_type": "Black Cotton", "rainfall_required": "50–100 mm", "temp_required": "25–40°C"},
            ]

        # ── Step 4: Price data ─────────────────────────────────────────────
        price_data = get_price_data()

        # ── Step 5: Profit calculation ─────────────────────────────────────
        profit_data = calculate_profit(crops, price_data, acres)

        # ── Step 6: AI agricultural advice ────────────────────────────────
        advice = generate_agricultural_advice(soil_data, crops, profit_data, state, api_key, language)

        # ── Step 7: Best crop ──────────────────────────────────────────────
        best_crop = get_best_crop(profit_data)

        # ── Build response ─────────────────────────────────────────────────
        response_data = {
            "success": True,
            "image_path": f"/static/uploads/{unique_name}",
            "soil_analysis": soil_data,
            "climate": climate,
            "location": {"state": state, "district": district},
            "recommended_crops": crops,
            "profit_analysis": profit_data,
            "best_crop": best_crop,
            "advice": advice,
            "acres": acres,
            "language": language
        }

        # Store in session for results page
        session["last_result"] = json.dumps(response_data)

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


@app.route("/results")
def results():
    """Results page — loads data from session."""
    result_json = session.get("last_result")
    if not result_json:
        return render_template("results.html", data=None)

    data = json.loads(result_json)
    return render_template("results.html", data=data)


@app.route("/api/translate", methods=["POST"])
def api_translate():
    """Translate a block of text to target language."""
    payload = request.get_json()
    text = payload.get("text", "")
    target = payload.get("language", "en")
    api_key = GEMINI_API_KEY

    translated = translate_text(text, target, api_key)
    return jsonify({"translated": translated})


@app.route("/api/weather", methods=["POST"])
def api_weather():
    """Get weather insights for a location."""
    payload = request.get_json()
    state = payload.get("state", "Tamil Nadu")
    district = payload.get("district", "")
    api_key = GEMINI_API_KEY

    insights = get_weather_insights(state, district, api_key)
    return jsonify(insights)


@app.route("/api/states")
def api_states():
    return jsonify({"states": INDIAN_STATES})


# ─── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  AI Smart Crop Recommendation & Profit Prediction System")
    print("  Team: Penin, Thirupathi, Mallikarjuna")
    print("  Dhanalakshmi Srinivasan University")
    print("=" * 60)
    print("  Server running at: http://localhost:5000")
    print("  Set GEMINI_API_KEY environment variable or enter in the app")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
