# 🌾 AI-Based Smart Crop Recommendation & Profit Prediction System

**Developed by:** Penin, Thirupathi, Mallikarjuna  
**University:** Dhanalakshmi Srinivasan University

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Your Gemini API Key
Get a free key from [Google AI Studio](https://aistudio.google.com/apikey).

**Option A** — Environment variable (recommended):
```bash
# Windows CMD
set GEMINI_API_KEY=your_api_key_here

# Windows PowerShell
$env:GEMINI_API_KEY="your_api_key_here"
```

**Option B** — Enter directly in the web app's API Key field.

### 3. Run the Application
```bash
python app.py
```

Open your browser at: **http://localhost:5000**

---

## 📁 Project Structure

```
AGRI_PROJECT/
├── app.py                  # Flask backend (main server)
├── requirements.txt        # Python dependencies
├── README.md
│
├── templates/
│   ├── index.html          # Home page (upload + location form)
│   └── results.html        # Analysis results dashboard
│
├── static/
│   ├── css/
│   │   └── style.css       # Professional Royal theme
│   ├── js/
│   │   └── main.js         # Chart.js + UI interactions
│   ├── images/             # Static images
│   └── uploads/            # Uploaded land images (auto-created)
│
├── models/
│   ├── crop_dataset.csv    # Crop soil/climate/yield data
│   └── price_dataset.csv   # Market price data
│
└── utils/
    ├── __init__.py
    ├── vision.py           # OpenCV + Gemini Vision soil analysis
    ├── prediction.py       # Crop recommendation engine
    ├── profit_calc.py      # Profit calculation logic
    └── gemini_ai.py        # Gemini AI advice + translation
```

---

## 🔧 Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python Flask |
| AI/Vision | Google Gemini 2.0 Flash API |
| Computer Vision | OpenCV |
| Charts | Chart.js 4 |
| Frontend | HTML5 + Bootstrap 5 |
| Data | Pandas + CSV datasets |

---

## 🌟 Features

1. **Land Image Analysis** — Upload a soil/land photo; OpenCV + Gemini Vision detect soil type, color, texture, moisture, pH, drainage
2. **Location-Based Climate Data** — State/district input fetches regional rainfall, temperature, and season
3. **Crop Recommendation Engine** — Ranks 25+ crops by suitability score based on soil & climate match
4. **Yield Prediction** — Estimates kg per acre from historical dataset
5. **Market Price Integration** — Indian MSP/market prices for all crops
6. **Profit Calculator** — Revenue, cost, profit & ROI for each crop
7. **Interactive Charts** — Bar chart (Revenue vs Profit), Yield comparison, ROI doughnut
8. **AI Expert Advice** — Gemini generates farming risks, irrigation, fertilizer, market tips
9. **Multilingual Support** — English, Tamil, Hindi, Telugu, Kannada
10. **GPS Auto-detect** — Browser geolocation for automatic coordinates

---

## 🎨 UI Theme

- **Primary:** Deep Green `#1B5E20`
- **Gold:** Royal Gold `#C9A227`  
- **Accent:** Dark Blue `#0D47A1`
- **Background:** Light Cream `#F5F5F5`
- **Fonts:** Playfair Display (headings) + Inter (body)

---

## 📊 Supported Crops

Paddy, Wheat, Maize, Groundnut, Cotton, Sugarcane, Millet, Sorghum, Soybean, Turmeric, Banana, Tomato, Onion, Chilli, Sunflower

---

## 🔑 API Key Note

This application uses **Google Gemini 2.0 Flash** API. The free tier provides generous usage limits suitable for this project. Get your key at [aistudio.google.com](https://aistudio.google.com/apikey).
