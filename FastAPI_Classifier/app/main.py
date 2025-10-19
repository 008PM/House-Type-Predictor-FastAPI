from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import joblib
import json
import os

# Import the AI generator
from .ai_report_generator import AIReportGenerator

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
    title="BKW AI Planning Assistant API",
    description=(
        "AI-powered building planning API with:\n"
        "1️⃣ `/predict` — Predicts Room_Type_No\n"
        "2️⃣ `/predict-load` — Predicts Heating & Cooling loads\n"
        "3️⃣ `/generate_report` — AI-powered report generation with Claude Sonnet 4.5"
    ),
    version="2.0"
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
# Define input schemas
# -------------------------------
class RoomFeatures(BaseModel):
    volume_m3: float
    area_m2: float
    total_heating_load_kw: float

class ReportRequest(BaseModel):
    project_name: str
    location: str
    project_type: str
    federal_state: str

# -------------------------------
# Root endpoint for health check
# -------------------------------
@app.get("/")
def root():
    """
    Health check endpoint - verifies API is running
    """
    return {
        "status": "online",
        "message": "BKW AI Planning Assistant API",
        "version": "2.0",
        "ai": "Powered by Claude Sonnet 4.5",
        "endpoints": {
            "predict_room_type": "/predict",
            "predict_load": "/predict-load",
            "generate_report": "/generate_report (AI-powered)",
            "docs": "/docs"
        }
    }

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

# -------------------------------
# 3️⃣ AI Report Generation Endpoint
# -------------------------------
@app.post("/generate_report", summary="Generate AI-Powered Report")
async def generate_ai_report(
    request: str = Form(...),
    room_book: Optional[UploadFile] = File(None),
    cost_estimate: Optional[UploadFile] = File(None),
    export_format: str = Form("docx")
):
    """
    Generate AI-powered Erläuterungsbericht using Claude Sonnet 4.5
    
    🤖 Powered by Anthropic Claude API
    
    **Required (as JSON in 'request' field):**
    ```json
    {
        "project_name": "Neubau Zentrale Muster GmbH",
        "location": "Stuttgart, Baden-Württemberg",
        "project_type": "office",
        "federal_state": "Baden-Württemberg"
    }
    ```
    
    **Optional files:**
    - room_book: Excel file with room data
    - cost_estimate: Excel file with cost data
    
    **Export format:** "docx" (default) or "markdown"
    """
    try:
        # Parse request
        req_data = json.loads(request)
        req = ReportRequest(**req_data)
        
        print(f"\n{'='*60}")
        print(f"🚀 Starting AI Report Generation")
        print(f"   Project: {req.project_name}")
        print(f"   Type: {req.project_type}")
        print(f"{'='*60}\n")
        
        # Initialize AI generator
        try:
            generator = AIReportGenerator(
                project_name=req.project_name,
                location=req.location,
                project_type=req.project_type,
                federal_state=req.federal_state
            )
        except ValueError as e:
            raise HTTPException(
                status_code=500,
                detail=f"{str(e)} - Please set ANTHROPIC_API_KEY environment variable"
            )
        
        # Load optional data files
        if room_book:
            generator.load_room_book(room_book)
        if cost_estimate:
            generator.load_cost_estimate(cost_estimate)
        
        # Generate report with AI
        report = generator.generate_report()
        
        # Export in requested format
        if export_format == "markdown":
            file_path = generator.export_markdown(report)
            media_type = "text/markdown"
        else:  # docx
            file_path = generator.export_docx(report)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        
        filename = os.path.basename(file_path)
        
        print(f"\n{'='*60}")
        print(f"✅ Report Generation Complete!")
        print(f"   File: {filename}")
        print(f"{'='*60}\n")
        
        return FileResponse(
            file_path,
            filename=filename,
            media_type=media_type
        )
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in request field")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation error: {e}")
