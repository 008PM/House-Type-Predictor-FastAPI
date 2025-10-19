# 🏠 House Type Predictor - FastAPI

Eine Machine-Learning-API zur Vorhersage von Raumtypen basierend auf physikalischen Eigenschaften (Volumen, Fläche, Heizlast).

## 📋 Projekt-Übersicht

Dieses Projekt besteht aus:
- **FastAPI Backend** - REST API mit trainiertem ML-Modell
- **Machine Learning Model** - Scikit-learn basierter Klassifikator
- **Railway Deployment** - Production-ready Konfiguration
- **Next.js Integration** - Frontend-Beispielcode

## 🚀 Quick Start

### Lokale Entwicklung

```bash
# Virtual Environment erstellen und aktivieren
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt

# Server starten (aus dem Projekt-Root)
uvicorn FastAPI_Classifier.app.main:app --reload

# ODER: Im FastAPI_Classifier Ordner
cd FastAPI_Classifier
uvicorn app.main:app --reload
```

Öffnen Sie http://127.0.0.1:8000/docs für die interaktive API-Dokumentation.

## 📦 Deployment

### Railway Deployment (empfohlen)

Das Projekt verwendet **Railpack** - Railways moderner Zero-Config Builder:

1. Pushen Sie das Projekt zu GitHub
2. Verbinden Sie Ihr Repository mit [Railway](https://railway.app)
3. Railpack erkennt automatisch Python und baut Ihre App
4. Nach ~2-4 Minuten ist Ihre API live!

**Build-Methode**: Railpack (Nachfolger von Nixpacks)

**Vorteile**:
- ✅ Zero-Config - automatische Erkennung
- ✅ Schnellere Builds durch besseres Caching
- ✅ Kleinere Container-Images

**Detaillierte Anleitung**: Siehe [DEPLOYMENT.md](DEPLOYMENT.md)

## 🎨 Frontend Integration

Vollständige Next.js Beispiele finden Sie in [NEXTJS_EXAMPLE.md](NEXTJS_EXAMPLE.md)

### Schnelles Beispiel:

```typescript
const response = await fetch('https://ihre-api.railway.app/predict', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    volume_m3: 50.5,
    area_m2: 25.0,
    total_heating_load_kw: 3.5
  })
});

const data = await response.json();
console.log(`Raumtyp: ${data.Room_Type_No}`);
```

## 📡 API Endpoints

| Endpoint | Method | Beschreibung |
|----------|--------|--------------|
| `/` | GET | Health Check |
| `/docs` | GET | Swagger UI (API Dokumentation) |
| `/predict` | POST | Raumtyp Vorhersage |

### Beispiel Request:

```bash
curl -X POST https://ihre-api.railway.app/predict \
  -H "Content-Type: application/json" \
  -d '{
    "volume_m3": 50.5,
    "area_m2": 25.0,
    "total_heating_load_kw": 3.5
  }'
```

### Beispiel Response:

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

## 🛠 Tech Stack

- **FastAPI** 0.115.0 - Modernes Web-Framework
- **Uvicorn** 0.30.6 - ASGI Server
- **Scikit-learn** 1.5.2 - Machine Learning
- **Pandas** 2.2.3 - Datenverarbeitung
- **Joblib** 1.4.2 - Model Serialisierung

## 📁 Projekt-Struktur

```
House-Type-Predictor-FastAPI/
├── FastAPI_Classifier/
│   ├── __init__.py             # Python Package Marker
│   ├── app/
│   │   ├── __init__.py         # Python Package Marker
│   │   ├── main.py             # FastAPI Anwendung
│   │   └── model/
│   │       └── room_type_predictor.joblib  # Trainiertes ML-Modell
│   ├── requirements.txt        # Python Dependencies (lokal)
│   └── ReadMe.md              # API Dokumentation
├── Misc_testing/              # Datenanalyse & Notebooks
├── requirements.txt           # Python Dependencies (Railpack)
├── Procfile                  # Alternativer Start-Command
├── railway.toml              # Railway Konfiguration (Railpack)
├── .gitignore               # Git Ignore Datei
├── DEPLOYMENT.md            # Deployment Guide
├── NEXTJS_EXAMPLE.md        # Frontend Integration
└── README.md                # Diese Datei
```

## 🔒 CORS Konfiguration

Die API ist bereits für Cross-Origin-Requests konfiguriert. Für Produktion sollten Sie spezifische Origins in `FastAPI_Classifier/app/main.py` festlegen:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ihre-nextjs-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📊 Machine Learning Modell

Das Modell wurde trainiert auf:
- **Input Features**: Volumen (m³), Fläche (m²), Heizlast (kW)
- **Output**: Raumtyp-Nummer (Klassifikation)
- **Framework**: Scikit-learn
- **Format**: Joblib-serialisiert

## 🧪 Testing

```bash
# API lokal testen
curl http://localhost:8000/

# Prediction testen
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"volume_m3": 50.5, "area_m2": 25.0, "total_heating_load_kw": 3.5}'
```

## 📝 Lizenz

Dieses Projekt ist für Bildungs- und Demonstrationszwecke erstellt.

## 🤝 Beitragen

Vorschläge und Pull Requests sind willkommen!

## 📞 Support

Bei Fragen oder Problemen öffnen Sie bitte ein Issue im Repository.

---

**Status**: ✅ Production Ready | 🚀 Railway Deployable | 🎨 Frontend Ready


