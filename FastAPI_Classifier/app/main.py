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
        "3️⃣ `/generate_report` — AI-powered report generation with Claude Sonnet 4.5\n"
        "4️⃣ `/estimate-costs` — AI-powered cost estimation (fast, JSON response)"
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

class CostEstimationRequest(BaseModel):
    project_name: str
    location: str
    project_type: str
    federal_state: str
    total_area_m2: float
    number_of_rooms: Optional[int] = None
    building_height_m: Optional[float] = None

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
            "estimate_costs": "/estimate-costs (AI-powered)",
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

# -------------------------------
# 4️⃣ AI Cost Estimation Endpoint
# -------------------------------
@app.post("/estimate-costs", summary="AI-powered Cost Estimation")
async def estimate_costs(request: CostEstimationRequest):
    """
    Generate AI-powered cost estimation for TGA (Technical Building Equipment)
    
    🤖 Uses Claude Sonnet 4.5 for intelligent cost calculation
    
    Returns detailed cost breakdown by cost groups (KG 410, 420, 430, 440, 470, 480)
    
    **Example Request:**
    ```json
    {
        "project_name": "Bürogebäude Muster GmbH",
        "location": "München, Bayern",
        "project_type": "office",
        "federal_state": "Bayern",
        "total_area_m2": 1500.0,
        "number_of_rooms": 50,
        "building_height_m": 12.0
    }
    ```
    """
    try:
        print(f"\n{'='*60}")
        print(f"💰 Starting AI Cost Estimation")
        print(f"   Project: {request.project_name}")
        print(f"   Area: {request.total_area_m2} m²")
        print(f"{'='*60}\n")
        
        # Initialize AI generator
        try:
            generator = AIReportGenerator(
                project_name=request.project_name,
                location=request.location,
                project_type=request.project_type,
                federal_state=request.federal_state
            )
        except ValueError as e:
            raise HTTPException(
                status_code=500,
                detail=f"{str(e)} - Please set ANTHROPIC_API_KEY environment variable"
            )
        
        # Build context for cost estimation
        context = f"""
PROJEKT KOSTENSCHÄTZUNG:

Projektname: {request.project_name}
Standort: {request.location}
Gebäudetyp: {request.project_type}
Bundesland: {request.federal_state}

GEBÄUDEDATEN:
- Gesamtfläche: {request.total_area_m2} m²
- Anzahl Räume: {request.number_of_rooms or 'nicht angegeben'}
- Gebäudehöhe: {request.building_height_m or 'nicht angegeben'} m
"""
        
        # AI Prompt für Kostenschätzung
        prompt = f"""{context}

Erstelle eine detaillierte Kostenschätzung für die Technische Gebäudeausrüstung (TGA) nach DIN 276.

Berechne für jede Kostengruppe:

**KG 410 - Abwasser-, Wasser- und Gasanlagen**
- Berücksichtige: Sanitärobjekte, Leitungen, Armaturen
- Richtwert: 80-120 €/m² für {request.project_type}

**KG 420 - Wärmeversorgungsanlagen**
- Wärmeerzeugung, Verteilung, Übergabe
- Richtwert: 120-180 €/m² für {request.project_type}

**KG 430 - Lüftungstechnische Anlagen**
- RLT-Anlagen, Kanäle, Luftauslässe
- Richtwert: 100-150 €/m² für {request.project_type}

**KG 434 - Kältetechnische Anlagen**
- Nur wenn erforderlich
- Richtwert: 60-100 €/m² für {request.project_type}

**KG 440 - Elektroanlagen**
- Stromversorgung, Beleuchtung, IT
- Richtwert: 100-140 €/m² für {request.project_type}

**KG 470 - Nutzungsspezifische Anlagen**
- Feuerlöschanlage, Sonderausstattung
- Richtwert: 20-40 €/m² für {request.project_type}

**KG 480 - Gebäudeautomation**
- DDC-System, Regelung, Visualisierung
- Richtwert: 30-50 €/m² für {request.project_type}

WICHTIG:
1. Gib für JEDE Kostengruppe einen spezifischen €-Betrag an (nicht nur Richtwerte)
2. Begründe die Wahl (einfacher/mittlerer/gehobener Standard)
3. Berücksichtige den Standort {request.federal_state} (Lohnniveau)
4. Berücksichtige den Gebäudetyp {request.project_type}
5. Summiere am Ende die Gesamtkosten TGA (KG 400)

Format als JSON:
{{
  "kg_410": {{"betrag": 00000, "pro_m2": 000, "beschreibung": "..."}},
  "kg_420": {{"betrag": 00000, "pro_m2": 000, "beschreibung": "..."}},
  "kg_430": {{"betrag": 00000, "pro_m2": 000, "beschreibung": "..."}},
  "kg_434": {{"betrag": 00000, "pro_m2": 000, "beschreibung": "..."}},
  "kg_440": {{"betrag": 00000, "pro_m2": 000, "beschreibung": "..."}},
  "kg_470": {{"betrag": 00000, "pro_m2": 000, "beschreibung": "..."}},
  "kg_480": {{"betrag": 00000, "pro_m2": 000, "beschreibung": "..."}},
  "gesamt_kg_400": {{"betrag": 00000, "pro_m2": 000}},
  "genauigkeit": "±30% (Kostenschätzung nach LP2)",
  "hinweise": ["...", "..."]
}}
"""
        
        # Call Claude AI
        print("🤖 Calling Claude Sonnet 4.5 for cost estimation...")
        response = generator._call_claude(prompt, max_tokens=2000)
        
        # Parse JSON response
        import re
        
        # Extract JSON from response (might have markdown code blocks)
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            cost_data = json.loads(json_match.group(0))
        else:
            cost_data = {"error": "Could not parse AI response", "raw_response": response}
        
        print(f"\n{'='*60}")
        print(f"✅ Cost Estimation Complete!")
        print(f"   Total: {cost_data.get('gesamt_kg_400', {}).get('betrag', 'N/A')} €")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "project_name": request.project_name,
            "total_area_m2": request.total_area_m2,
            "cost_estimation": cost_data,
            "generated_by": "Claude Sonnet 4.5",
            "disclaimer": "Kostenschätzung nach DIN 276, Genauigkeit ±30%, Stand LP2"
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response as JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cost estimation error: {str(e)}")
