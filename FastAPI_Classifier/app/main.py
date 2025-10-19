from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# -------------------------------
# Load the model
# -------------------------------
#BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#MODEL_PATH = os.path.join(BASE_DIR, "model", "room_type_predictor.joblib")
#model = joblib.load(MODEL_PATH)

# -------------------------------
# Initialize FastAPI
# -------------------------------
app = FastAPI(
    title="Room Type Predictor API",
    description="Predict Room_Type_No from 3 numerical inputs",
    version="1.0"
)

# -------------------------------
# Configure CORS for Next.js Frontend
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion: Ihre Next.js Domain eintragen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Load both models
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model")

try:
    model_room_type = joblib.load(os.path.join(MODEL_DIR, "room_type_predictor.joblib"))
except Exception as e:
    raise RuntimeError(f"❌ Error loading room_type_predictor.joblib: {e}")

try:
    model_room_load = joblib.load(os.path.join(MODEL_DIR, "room_load_predictor.joblib"))
except Exception as e:
    raise RuntimeError(f"❌ Error loading room_load_predictor.joblib: {e}")

# -------------------------------
# Initialize FastAPI
# -------------------------------
app = FastAPI(
    title="Room Prediction API",
    description=(
        "API with 2 endpoints:\n"
        "1️⃣ `/predict` — Predicts `Room_Type_No` based on volume, area, and heating load.\n"
        "2️⃣ `/predict-load` — Predicts `Heating_W_per_m2` and `Cooling_W_per_m2` from the same features."
    ),
    version="2.0"
)

# -------------------------------
# Define input schema
# -------------------------------
class RoomFeatures(BaseModel):
    volume_m3: float
    area_m2: float
    total_heating_load_kw: float

# -------------------------------
# 1️⃣ Predict Room Type Endpoint
# -------------------------------
@app.post("/predict", summary="Predict Room Type Number")
def predict_room_type(features: RoomFeatures):
    """
    Predict `Room_Type_No` from:
    - volume_m3
    - area_m2
    - total_heating_load_kw
    """
    try:
        input_data = [[
            features.volume_m3,
            features.area_m2,
            features.total_heating_load_kw
        ]]
        prediction = model_room_type.predict(input_data)
        return {"Room_Type_No": int(prediction[0])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")

# -------------------------------
# 2️⃣ Predict Load Endpoint
# -------------------------------
@app.post("/predict-load", summary="Predict Heating and Cooling Load")
def predict_room_load(features: RoomFeatures):
    """
    Predict:
    - Heating_W_per_m2
    - Cooling_W_per_m2
    from:
    - volume_m3
    - area_m2
    - total_heating_load_kw
    """
    try:
        input_data = [[
            features.volume_m3,
            features.area_m2,
            features.total_heating_load_kw
        ]]
        output = model_room_load.predict(input_data)[0]  # expect 2 outputs
        return {
            "Heating_W_per_m2": float(output[0]),
            "Cooling_W_per_m2": float(output[1])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Load prediction error: {e}")
