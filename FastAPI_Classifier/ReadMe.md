# Room Type Predictor API

FastAPI-basierte Machine Learning API zur Vorhersage von Raumtypen basierend auf physikalischen Merkmalen.

## 🚀 Lokale Entwicklung

### 1️⃣ Virtual Environment erstellen
```bash
python3 -m venv .venv
```

### 2️⃣ Aktivieren
```bash
source .venv/bin/activate        # Mac/Linux
# ODER auf Windows:
.venv\Scripts\activate
```

### 3️⃣ Dependencies installieren
```bash
pip install -r requirements.txt
```

### 4️⃣ Server starten
```bash
cd FastAPI_Classifier
uvicorn app.main:app --reload
```

### 5️⃣ API testen
- **Swagger UI**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/
- **ReDoc**: http://127.0.0.1:8000/redoc

## 📦 Railway Deployment

Siehe **[DEPLOYMENT.md](../DEPLOYMENT.md)** für vollständige Anleitung zum Deployen auf Railway.

## 🎨 Next.js Integration

Siehe **[NEXTJS_EXAMPLE.md](../NEXTJS_EXAMPLE.md)** für vollständigen Frontend-Code und Integration.

## 📡 API Endpoints

### `GET /`
Health Check Endpoint
```json
{
  "status": "ok",
  "message": "Room Type Predictor API is running"
}
```

### `POST /predict`
Raumtyp Vorhersage

**Request Body:**
```json
{
  "volume_m3": 50.5,
  "area_m2": 25.0,
  "total_heating_load_kw": 3.5
}
```

**Response:**
```json
{
  "Room_Type_No": 2,
  "input": {
    "volume_m3": 50.5,
    "area_m2": 25.0,
    "total_heating_load_kw": 3.5
  }
}
```