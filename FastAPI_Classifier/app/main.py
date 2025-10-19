from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import os

# -------------------------------
# Load the model
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "room_type_predictor.joblib")
model = joblib.load(MODEL_PATH)

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
# Define input schema
# -------------------------------
class RoomFeatures(BaseModel):
    volume_m3: float
    area_m2: float
    total_heating_load_kw: float

# -------------------------------
# Root endpoint for health check
# -------------------------------
@app.get("/")
def root():
    """
    Health check endpoint
    """
    return {"status": "ok", "message": "Room Type Predictor API is running"}

# -------------------------------
# Create prediction endpoint
# -------------------------------
@app.post("/predict")
def predict_room_type(features: RoomFeatures):
    """
    Predict Room_Type_No from 3 numerical inputs
    """
    input_data = [[
        features.volume_m3,
        features.area_m2,
        features.total_heating_load_kw
    ]]
    prediction = model.predict(input_data)
    return {
        "Room_Type_No": int(prediction[0]),
        "input": {
            "volume_m3": features.volume_m3,
            "area_m2": features.area_m2,
            "total_heating_load_kw": features.total_heating_load_kw
        }
    }
