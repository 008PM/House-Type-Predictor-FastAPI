# 🎨 Next.js Frontend Integration - ML Predictions

## Beispiel-Code für Ihr Next.js Projekt

Diese Anleitung zeigt beide ML-Endpoints:
- `/predict` - Raumtyp Vorhersage
- `/predict-load` - Heiz-/Kühllast Vorhersage

### 1. API Client erstellen

Erstellen Sie `lib/api.ts`:

```typescript
// lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface RoomFeatures {
  volume_m3: number;
  area_m2: number;
  total_heating_load_kw: number;
}

export interface PredictionResponse {
  Room_Type_No: number;
}

export interface LoadPredictionResponse {
  Heating_W_per_m2: number;
  Cooling_W_per_m2: number;
}

// 1️⃣ Predict Room Type
export async function predictRoomType(
  features: RoomFeatures
): Promise<PredictionResponse> {
  const response = await fetch(`${API_URL}/predict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(features),
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }

  return response.json();
}

// 2️⃣ Predict Heating & Cooling Load
export async function predictLoad(
  features: RoomFeatures
): Promise<LoadPredictionResponse> {
  const response = await fetch(`${API_URL}/predict-load`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(features),
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }

  return response.json();
}

// Health Check
export async function checkApiHealth(): Promise<{ status: string; message: string }> {
  const response = await fetch(`${API_URL}/`);
  return response.json();
}
```

### 2. Umgebungsvariable setzen

Erstellen Sie `.env.local`:

```bash
NEXT_PUBLIC_API_URL=https://ihr-projekt.railway.app
```

### 3. React Components erstellen

#### 3.1 Raumtyp Vorhersage

Erstellen Sie `components/RoomTypePredictor.tsx`:

```typescript
"use client";

import { useState } from "react";
import { predictRoomType, type RoomFeatures } from "@/lib/api";

export default function RoomTypePredictor() {
  const [features, setFeatures] = useState<RoomFeatures>({
    volume_m3: 0,
    area_m2: 0,
    total_heating_load_kw: 0,
  });
  const [prediction, setPrediction] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const result = await predictRoomType(features);
      setPrediction(result.Room_Type_No);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ein Fehler ist aufgetreten");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">
        Raumtyp Vorhersage
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Volumen (m³)
          </label>
          <input
            type="number"
            step="0.1"
            value={features.volume_m3}
            onChange={(e) =>
              setFeatures({ ...features, volume_m3: parseFloat(e.target.value) })
            }
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Fläche (m²)
          </label>
          <input
            type="number"
            step="0.1"
            value={features.area_m2}
            onChange={(e) =>
              setFeatures({ ...features, area_m2: parseFloat(e.target.value) })
            }
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Heizlast (kW)
          </label>
          <input
            type="number"
            step="0.1"
            value={features.total_heating_load_kw}
            onChange={(e) =>
              setFeatures({
                ...features,
                total_heating_load_kw: parseFloat(e.target.value),
              })
            }
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 transition-colors font-medium"
        >
          {loading ? "Wird berechnet..." : "Vorhersage starten"}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-md">
          <p className="font-medium">Fehler:</p>
          <p>{error}</p>
        </div>
      )}

      {prediction !== null && (
        <div className="mt-6 p-4 bg-green-100 border border-green-400 rounded-md">
          <p className="text-green-800 font-medium">Ergebnis:</p>
          <p className="text-2xl font-bold text-green-900">
            Raumtyp Nr. {prediction}
          </p>
        </div>
      )}
    </div>
  );
}
```

#### 3.2 Heiz-/Kühllast Vorhersage

Erstellen Sie `components/LoadPredictor.tsx`:

```typescript
"use client";

import { useState } from "react";
import { predictLoad, type RoomFeatures, type LoadPredictionResponse } from "@/lib/api";

export default function LoadPredictor() {
  const [features, setFeatures] = useState<RoomFeatures>({
    volume_m3: 0,
    area_m2: 0,
    total_heating_load_kw: 0,
  });
  const [prediction, setPrediction] = useState<LoadPredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const result = await predictLoad(features);
      setPrediction(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ein Fehler ist aufgetreten");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">
        🔥❄️ Heiz-/Kühllast Vorhersage
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Volumen (m³)
          </label>
          <input
            type="number"
            step="0.1"
            value={features.volume_m3}
            onChange={(e) =>
              setFeatures({ ...features, volume_m3: parseFloat(e.target.value) })
            }
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Fläche (m²)
          </label>
          <input
            type="number"
            step="0.1"
            value={features.area_m2}
            onChange={(e) =>
              setFeatures({ ...features, area_m2: parseFloat(e.target.value) })
            }
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Heizlast (kW)
          </label>
          <input
            type="number"
            step="0.1"
            value={features.total_heating_load_kw}
            onChange={(e) =>
              setFeatures({
                ...features,
                total_heating_load_kw: parseFloat(e.target.value),
              })
            }
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            required
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-gradient-to-r from-orange-600 to-cyan-600 text-white py-2 px-4 rounded-md hover:from-orange-700 hover:to-cyan-700 disabled:from-gray-400 disabled:to-gray-500 transition-colors font-medium"
        >
          {loading ? "Wird berechnet..." : "Last berechnen"}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-md">
          <p className="font-medium">Fehler:</p>
          <p>{error}</p>
        </div>
      )}

      {prediction !== null && (
        <div className="mt-6 space-y-3">
          <div className="p-4 bg-orange-100 border border-orange-400 rounded-md">
            <p className="text-orange-800 font-medium">🔥 Heizlast:</p>
            <p className="text-2xl font-bold text-orange-900">
              {prediction.Heating_W_per_m2.toFixed(1)} W/m²
            </p>
          </div>
          
          <div className="p-4 bg-cyan-100 border border-cyan-400 rounded-md">
            <p className="text-cyan-800 font-medium">❄️ Kühllast:</p>
            <p className="text-2xl font-bold text-cyan-900">
              {prediction.Cooling_W_per_m2.toFixed(1)} W/m²
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
```

#### 3.3 Kombiniertes Component (beide Predictions)

Erstellen Sie `components/RoomPredictor.tsx` für beide Features zusammen:

```typescript
"use client";

import { useState } from "react";
import { predictRoomType, predictLoad, type RoomFeatures } from "@/lib/api";

export default function RoomPredictor() {
  const [features, setFeatures] = useState<RoomFeatures>({
    volume_m3: 0,
    area_m2: 0,
    total_heating_load_kw: 0,
  });
  
  const [roomType, setRoomType] = useState<number | null>(null);
  const [loads, setLoads] = useState<{ heating: number; cooling: number } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Beide Predictions parallel ausführen
      const [typeResult, loadResult] = await Promise.all([
        predictRoomType(features),
        predictLoad(features),
      ]);
      
      setRoomType(typeResult.Room_Type_No);
      setLoads({
        heating: loadResult.Heating_W_per_m2,
        cooling: loadResult.Cooling_W_per_m2,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ein Fehler ist aufgetreten");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-3xl font-bold mb-6 text-gray-800">
        🏠 Raum-Analyse System
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4 mb-6">
        <div className="grid md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Volumen (m³)
            </label>
            <input
              type="number"
              step="0.1"
              value={features.volume_m3}
              onChange={(e) =>
                setFeatures({ ...features, volume_m3: parseFloat(e.target.value) })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Fläche (m²)
            </label>
            <input
              type="number"
              step="0.1"
              value={features.area_m2}
              onChange={(e) =>
                setFeatures({ ...features, area_m2: parseFloat(e.target.value) })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Heizlast (kW)
            </label>
            <input
              type="number"
              step="0.1"
              value={features.total_heating_load_kw}
              onChange={(e) =>
                setFeatures({
                  ...features,
                  total_heating_load_kw: parseFloat(e.target.value),
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-6 rounded-md hover:from-blue-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 transition-colors font-medium text-lg"
        >
          {loading ? "Analysiere..." : "🔍 Raum analysieren"}
        </button>
      </form>

      {error && (
        <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded-md mb-4">
          <p className="font-medium">❌ Fehler:</p>
          <p>{error}</p>
        </div>
      )}

      {(roomType !== null || loads !== null) && (
        <div className="grid md:grid-cols-3 gap-4">
          {/* Raumtyp */}
          {roomType !== null && (
            <div className="p-4 bg-blue-50 border-2 border-blue-400 rounded-lg">
              <p className="text-sm text-blue-700 font-medium mb-1">Raumtyp</p>
              <p className="text-3xl font-bold text-blue-900">Nr. {roomType}</p>
            </div>
          )}

          {/* Heizlast */}
          {loads !== null && (
            <div className="p-4 bg-orange-50 border-2 border-orange-400 rounded-lg">
              <p className="text-sm text-orange-700 font-medium mb-1">🔥 Heizlast</p>
              <p className="text-3xl font-bold text-orange-900">
                {loads.heating.toFixed(1)}
              </p>
              <p className="text-sm text-orange-600">W/m²</p>
            </div>
          )}

          {/* Kühllast */}
          {loads !== null && (
            <div className="p-4 bg-cyan-50 border-2 border-cyan-400 rounded-lg">
              <p className="text-sm text-cyan-700 font-medium mb-1">❄️ Kühllast</p>
              <p className="text-3xl font-bold text-cyan-900">
                {loads.cooling.toFixed(1)}
              </p>
              <p className="text-sm text-cyan-600">W/m²</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

### 4. Page Component (App Router)

#### Option A: Nur Raumtyp

Erstellen Sie `app/page.tsx`:

```typescript
import RoomTypePredictor from "@/components/RoomTypePredictor";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="container mx-auto">
        <h1 className="text-4xl font-bold text-center mb-8 text-gray-900">
          🏠 Raumtyp Vorhersage
        </h1>
        <RoomTypePredictor />
      </div>
    </main>
  );
}
```

#### Option B: Nur Heiz-/Kühllast

Erstellen Sie `app/loads/page.tsx`:

```typescript
import LoadPredictor from "@/components/LoadPredictor";

export default function LoadsPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-orange-50 to-cyan-50 py-12 px-4">
      <div className="container mx-auto">
        <h1 className="text-4xl font-bold text-center mb-8 text-gray-900">
          🔥❄️ Heiz-/Kühllast Berechnung
        </h1>
        <LoadPredictor />
      </div>
    </main>
  );
}
```

#### Option C: Kombiniert (empfohlen)

Erstellen Sie `app/page.tsx`:

```typescript
import RoomPredictor from "@/components/RoomPredictor";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-cyan-50 py-12 px-4">
      <div className="container mx-auto">
        <h1 className="text-4xl font-bold text-center mb-2 text-gray-900">
          🏠 Raum-Analyse System
        </h1>
        <p className="text-center text-gray-600 mb-8">
          ML-gestützte Vorhersage für Raumtyp, Heiz- und Kühllast
        </p>
        <RoomPredictor />
      </div>
    </main>
  );
}
```

### 5. Alternative: Server Component mit Server Actions

Für Next.js App Router mit Server Actions:

```typescript
// app/actions.ts
"use server";

import { predictRoomType, type RoomFeatures } from "@/lib/api";

export async function makePrediction(formData: FormData) {
  const features: RoomFeatures = {
    volume_m3: parseFloat(formData.get("volume_m3") as string),
    area_m2: parseFloat(formData.get("area_m2") as string),
    total_heating_load_kw: parseFloat(formData.get("total_heating_load_kw") as string),
  };

  try {
    const result = await predictRoomType(features);
    return { success: true, data: result };
  } catch (error) {
    return { 
      success: false, 
      error: error instanceof Error ? error.message : "Fehler aufgetreten" 
    };
  }
}
```

### 6. Tailwind CSS Setup

Falls noch nicht vorhanden, installieren Sie Tailwind:

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

Konfigurieren Sie `tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
```

### 7. TypeScript Konfiguration

Stellen Sie sicher, dass `tsconfig.json` die paths enthält:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

## Deployment des Next.js Frontends

### Option 1: Vercel (empfohlen)
```bash
npm install -g vercel
vercel
```

### Option 2: Netlify
```bash
npm run build
# Deployen Sie den .next Ordner
```

### Option 3: Railway (beide im selben Account)
- Erstellen Sie ein separates Railway Projekt für Next.js
- Verbinden Sie es mit Ihrem Frontend-Repository

## Wichtige Hinweise

1. **CORS**: Die FastAPI ist bereits so konfiguriert, dass sie alle Origins akzeptiert (`allow_origins=["*"]`)
   
2. **Produktions-CORS**: Für Produktion sollten Sie in `FastAPI_Classifier/app/main.py` die spezifische Domain eintragen:
   ```python
   allow_origins=["https://ihre-nextjs-app.vercel.app"]
   ```

3. **Environment Variables**: Vergessen Sie nicht, `NEXT_PUBLIC_API_URL` in Ihren Deployment-Settings zu setzen

4. **Error Handling**: Der Beispielcode enthält grundlegendes Error Handling. Erweitern Sie es nach Bedarf.

## 🧪 Testing lokal

1. **FastAPI Backend lokal starten:**
   ```bash
   cd FastAPI_Classifier
   uvicorn app.main:app --reload
   ```

2. **Next.js Frontend lokal starten:**
   ```bash
   npm run dev
   ```

3. **`.env.local` sollte enthalten:**
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Test beide Endpoints:**
   ```bash
   # Raumtyp Vorhersage
   curl -X POST http://localhost:8000/predict \
     -H "Content-Type: application/json" \
     -d '{"volume_m3": 50.5, "area_m2": 25.0, "total_heating_load_kw": 3.5}'

   # Heiz-/Kühllast Vorhersage  
   curl -X POST http://localhost:8000/predict-load \
     -H "Content-Type: application/json" \
     -d '{"volume_m3": 50.5, "area_m2": 25.0, "total_heating_load_kw": 3.5}'
   ```

## 📊 Beispiel-Response

### `/predict` Response:
```json
{
  "Room_Type_No": 2
}
```

### `/predict-load` Response:
```json
{
  "Heating_W_per_m2": 45.3,
  "Cooling_W_per_m2": 28.7
}
```

## 🎨 UI Varianten

### Einfach (Separate Components)
- `RoomTypePredictor` - Nur Raumtyp
- `LoadPredictor` - Nur Lasten

### Kombiniert (Empfohlen)
- `RoomPredictor` - Beide Predictions parallel
- Schönere UX
- Weniger Requests

## 💡 Performance-Tipps

- **Parallel Requests**: Verwenden Sie `Promise.all()` für beide Predictions
- **Caching**: React Query oder SWR für besseres Caching
- **Debouncing**: Bei Live-Updates während Eingabe

## 🚀 Next Steps

- AI Features nutzen: Siehe `NEXTJS_AI_REPORT_EXAMPLE.md`
- Kostenschätzung: Siehe `NEXTJS_COST_ESTIMATION.md`


