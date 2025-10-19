# 💰 KI-gestützte Kostenschätzung - Next.js Integration

Anleitung zur Verwendung von Claude Sonnet 4.5 für intelligente Kostenschätzungen in Ihrer Next.js Anwendung.

## 🎯 Zwei Ansätze für Kostenschätzung

### Ansatz 1: Im Report enthalten (einfach)
Die Kostenschätzung ist bereits Teil des AI-Reports (`/generate_report`)

### Ansatz 2: Dedizierter Endpoint (empfohlen)
Erstellen Sie einen speziellen `/estimate-costs` Endpoint für schnellere, fokussierte Kostenschätzungen

---

## 📋 Ansatz 1: Kostenschätzung im Report

Der bestehende `/generate_report` Endpoint enthält automatisch eine Kostenschätzung im Abschnitt "B. Kostenschätzung".

### Next.js Implementierung

```typescript
// lib/api.ts
export interface CostEstimateRequest {
  project_name: string;
  location: string;
  project_type: "office" | "laboratory" | "hospital" | "school" | "residential";
  federal_state: string;
  cost_estimate_file?: File;  // Optional: Excel mit detaillierten Kosten
}

export async function generateReportWithCosts(
  request: CostEstimateRequest,
  format: "docx" | "markdown" = "markdown"
): Promise<Blob> {
  const formData = new FormData();
  formData.append("request", JSON.stringify(request));
  
  // Optional: Excel-Datei mit Kostendaten hochladen
  if (request.cost_estimate_file) {
    formData.append("cost_estimate", request.cost_estimate_file);
  }
  
  formData.append("export_format", format);
  
  const response = await fetch(`${API_URL}/generate_report`, {
    method: "POST",
    body: formData,
  });
  
  if (!response.ok) throw new Error("Report generation failed");
  return response.blob();
}
```

### React Component

```typescript
"use client";

import { useState } from "react";
import { generateReportWithCosts, downloadBlob } from "@/lib/api";

export default function SimpleCostEstimator() {
  const [projectData, setProjectData] = useState({
    project_name: "",
    location: "",
    project_type: "office" as const,
    federal_state: "Bayern",
  });
  const [costFile, setCostFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const blob = await generateReportWithCosts(
        {
          ...projectData,
          cost_estimate_file: costFile || undefined,
        },
        "markdown"  // Schneller als DOCX
      );
      
      downloadBlob(blob, "Kostenschaetzung.md");
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      {/* Formular-Felder hier */}
      <button type="submit" disabled={loading}>
        {loading ? "Generiere Kostenschätzung..." : "Kostenschätzung erstellen"}
      </button>
    </form>
  );
}
```

---

## 🚀 Ansatz 2: Dedizierter Kostenschätzungs-Endpoint (NEU)

Für schnellere, fokussierte Kostenschätzungen erstellen wir einen speziellen Endpoint.

### 1. FastAPI Endpoint erstellen

Fügen Sie zu `FastAPI_Classifier/app/main.py` hinzu:

```python
# Nach den bestehenden Endpoints hinzufügen

class CostEstimationRequest(BaseModel):
    project_name: str
    location: str
    project_type: str
    federal_state: str
    total_area_m2: float
    number_of_rooms: Optional[int] = None
    building_height_m: Optional[float] = None
    
@app.post("/estimate-costs", summary="AI-powered Cost Estimation")
async def estimate_costs(request: CostEstimationRequest):
    """
    Generate AI-powered cost estimation for TGA (Technical Building Equipment)
    
    🤖 Uses Claude Sonnet 4.5 for intelligent cost calculation
    
    Returns detailed cost breakdown by cost groups (KG 410, 420, 430, 440, 470, 480)
    """
    try:
        from .ai_report_generator import AIReportGenerator
        
        # Initialize AI generator
        generator = AIReportGenerator(
            project_name=request.project_name,
            location=request.location,
            project_type=request.project_type,
            federal_state=request.federal_state
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
        response = generator._call_claude(prompt, max_tokens=2000)
        
        # Parse JSON response
        import json
        import re
        
        # Extract JSON from response (might have markdown code blocks)
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            cost_data = json.loads(json_match.group(0))
        else:
            cost_data = {"error": "Could not parse AI response", "raw_response": response}
        
        return {
            "success": True,
            "project_name": request.project_name,
            "total_area_m2": request.total_area_m2,
            "cost_estimation": cost_data,
            "generated_by": "Claude Sonnet 4.5",
            "disclaimer": "Kostenschätzung nach DIN 276, Genauigkeit ±30%, Stand LP2"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cost estimation error: {str(e)}")
```

### 2. Next.js API Client

Fügen Sie zu `lib/api.ts` hinzu:

```typescript
export interface CostEstimationRequest {
  project_name: string;
  location: string;
  project_type: "office" | "laboratory" | "hospital" | "school" | "residential";
  federal_state: string;
  total_area_m2: number;
  number_of_rooms?: number;
  building_height_m?: number;
}

export interface CostGroup {
  betrag: number;
  pro_m2: number;
  beschreibung: string;
}

export interface CostEstimationResponse {
  success: boolean;
  project_name: string;
  total_area_m2: number;
  cost_estimation: {
    kg_410: CostGroup;
    kg_420: CostGroup;
    kg_430: CostGroup;
    kg_434: CostGroup;
    kg_440: CostGroup;
    kg_470: CostGroup;
    kg_480: CostGroup;
    gesamt_kg_400: { betrag: number; pro_m2: number };
    genauigkeit: string;
    hinweise: string[];
  };
  generated_by: string;
  disclaimer: string;
}

export async function estimateCosts(
  request: CostEstimationRequest
): Promise<CostEstimationResponse> {
  const response = await fetch(`${API_URL}/estimate-costs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Cost estimation failed");
  }

  return response.json();
}
```

### 3. React Component für Kostenschätzung

Erstellen Sie `components/CostEstimator.tsx`:

```typescript
"use client";

import { useState } from "react";
import { estimateCosts, type CostEstimationRequest, type CostEstimationResponse } from "@/lib/api";

const FEDERAL_STATES = [
  "Baden-Württemberg", "Bayern", "Berlin", "Brandenburg", "Bremen",
  "Hamburg", "Hessen", "Mecklenburg-Vorpommern", "Niedersachsen",
  "Nordrhein-Westfalen", "Rheinland-Pfalz", "Saarland", "Sachsen",
  "Sachsen-Anhalt", "Schleswig-Holstein", "Thüringen",
];

const PROJECT_TYPES = [
  { value: "office", label: "Bürogebäude" },
  { value: "laboratory", label: "Labor" },
  { value: "hospital", label: "Krankenhaus" },
  { value: "school", label: "Schule" },
  { value: "residential", label: "Wohngebäude" },
];

export default function CostEstimator() {
  const [formData, setFormData] = useState<CostEstimationRequest>({
    project_name: "",
    location: "",
    project_type: "office",
    federal_state: "Bayern",
    total_area_m2: 0,
    number_of_rooms: undefined,
    building_height_m: undefined,
  });

  const [result, setResult] = useState<CostEstimationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      console.log("🤖 Requesting AI cost estimation...");
      const estimation = await estimateCosts(formData);
      setResult(estimation);
      console.log("✅ Cost estimation complete!");
    } catch (err) {
      console.error("❌ Error:", err);
      setError(err instanceof Error ? err.message : "Ein Fehler ist aufgetreten");
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("de-DE", {
      style: "currency",
      currency: "EUR",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">
          💰 KI-Kostenschätzung
        </h2>
        <p className="text-gray-600 mb-6">
          Powered by Claude Sonnet 4.5 - Intelligente TGA-Kostenschätzung
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            {/* Projektname */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Projektname *
              </label>
              <input
                type="text"
                value={formData.project_name}
                onChange={(e) =>
                  setFormData({ ...formData, project_name: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            {/* Standort */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Standort *
              </label>
              <input
                type="text"
                value={formData.location}
                onChange={(e) =>
                  setFormData({ ...formData, location: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            {/* Gebäudetyp */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Gebäudetyp *
              </label>
              <select
                value={formData.project_type}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    project_type: e.target.value as CostEstimationRequest["project_type"],
                  })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              >
                {PROJECT_TYPES.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Bundesland */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Bundesland *
              </label>
              <select
                value={formData.federal_state}
                onChange={(e) =>
                  setFormData({ ...formData, federal_state: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              >
                {FEDERAL_STATES.map((state) => (
                  <option key={state} value={state}>
                    {state}
                  </option>
                ))}
              </select>
            </div>

            {/* Gesamtfläche */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Gesamtfläche (m²) *
              </label>
              <input
                type="number"
                step="0.1"
                min="0"
                value={formData.total_area_m2 || ""}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    total_area_m2: parseFloat(e.target.value) || 0,
                  })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            {/* Anzahl Räume (Optional) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Anzahl Räume (optional)
              </label>
              <input
                type="number"
                min="0"
                value={formData.number_of_rooms || ""}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    number_of_rooms: e.target.value ? parseInt(e.target.value) : undefined,
                  })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-green-600 to-blue-600 text-white py-3 px-6 rounded-md hover:from-green-700 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-500 transition-all font-medium text-lg shadow-md"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                KI berechnet Kosten...
              </span>
            ) : (
              "🤖 Kostenschätzung erstellen"
            )}
          </button>
        </form>

        {error && (
          <div className="mt-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-md">
            <p className="font-medium">❌ Fehler:</p>
            <p>{error}</p>
          </div>
        )}
      </div>

      {/* Results */}
      {result && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-2xl font-bold text-gray-800 mb-4">
            📊 Kostenschätzung: {result.project_name}
          </h3>

          <div className="grid gap-4 mb-6">
            {/* KG 410 */}
            <div className="bg-blue-50 p-4 rounded-md">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h4 className="font-bold text-gray-800">KG 410 - Sanitäranlagen</h4>
                  <p className="text-sm text-gray-600">
                    {result.cost_estimation.kg_410.beschreibung}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-blue-700">
                    {formatCurrency(result.cost_estimation.kg_410.betrag)}
                  </p>
                  <p className="text-sm text-gray-600">
                    {result.cost_estimation.kg_410.pro_m2} €/m²
                  </p>
                </div>
              </div>
            </div>

            {/* KG 420 */}
            <div className="bg-orange-50 p-4 rounded-md">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h4 className="font-bold text-gray-800">KG 420 - Wärmeversorgung</h4>
                  <p className="text-sm text-gray-600">
                    {result.cost_estimation.kg_420.beschreibung}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-orange-700">
                    {formatCurrency(result.cost_estimation.kg_420.betrag)}
                  </p>
                  <p className="text-sm text-gray-600">
                    {result.cost_estimation.kg_420.pro_m2} €/m²
                  </p>
                </div>
              </div>
            </div>

            {/* KG 430 */}
            <div className="bg-green-50 p-4 rounded-md">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h4 className="font-bold text-gray-800">KG 430 - Lüftungstechnik</h4>
                  <p className="text-sm text-gray-600">
                    {result.cost_estimation.kg_430.beschreibung}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-green-700">
                    {formatCurrency(result.cost_estimation.kg_430.betrag)}
                  </p>
                  <p className="text-sm text-gray-600">
                    {result.cost_estimation.kg_430.pro_m2} €/m²
                  </p>
                </div>
              </div>
            </div>

            {/* KG 434 */}
            <div className="bg-cyan-50 p-4 rounded-md">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h4 className="font-bold text-gray-800">KG 434 - Kältetechnik</h4>
                  <p className="text-sm text-gray-600">
                    {result.cost_estimation.kg_434.beschreibung}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-cyan-700">
                    {formatCurrency(result.cost_estimation.kg_434.betrag)}
                  </p>
                  <p className="text-sm text-gray-600">
                    {result.cost_estimation.kg_434.pro_m2} €/m²
                  </p>
                </div>
              </div>
            </div>

            {/* KG 440 */}
            <div className="bg-yellow-50 p-4 rounded-md">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h4 className="font-bold text-gray-800">KG 440 - Elektroanlagen</h4>
                  <p className="text-sm text-gray-600">
                    {result.cost_estimation.kg_440.beschreibung}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-yellow-700">
                    {formatCurrency(result.cost_estimation.kg_440.betrag)}
                  </p>
                  <p className="text-sm text-gray-600">
                    {result.cost_estimation.kg_440.pro_m2} €/m²
                  </p>
                </div>
              </div>
            </div>

            {/* KG 470 */}
            <div className="bg-red-50 p-4 rounded-md">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h4 className="font-bold text-gray-800">
                    KG 470 - Nutzungsspezifische Anlagen
                  </h4>
                  <p className="text-sm text-gray-600">
                    {result.cost_estimation.kg_470.beschreibung}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-red-700">
                    {formatCurrency(result.cost_estimation.kg_470.betrag)}
                  </p>
                  <p className="text-sm text-gray-600">
                    {result.cost_estimation.kg_470.pro_m2} €/m²
                  </p>
                </div>
              </div>
            </div>

            {/* KG 480 */}
            <div className="bg-purple-50 p-4 rounded-md">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h4 className="font-bold text-gray-800">KG 480 - Gebäudeautomation</h4>
                  <p className="text-sm text-gray-600">
                    {result.cost_estimation.kg_480.beschreibung}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-purple-700">
                    {formatCurrency(result.cost_estimation.kg_480.betrag)}
                  </p>
                  <p className="text-sm text-gray-600">
                    {result.cost_estimation.kg_480.pro_m2} €/m²
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Gesamtsumme */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-lg mb-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-xl font-bold">Gesamt TGA (KG 400)</h3>
                <p className="text-sm opacity-90">{result.cost_estimation.genauigkeit}</p>
              </div>
              <div className="text-right">
                <p className="text-4xl font-bold">
                  {formatCurrency(result.cost_estimation.gesamt_kg_400.betrag)}
                </p>
                <p className="text-lg">
                  {result.cost_estimation.gesamt_kg_400.pro_m2} €/m²
                </p>
              </div>
            </div>
          </div>

          {/* Hinweise */}
          {result.cost_estimation.hinweise && result.cost_estimation.hinweise.length > 0 && (
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
              <h4 className="font-bold text-yellow-800 mb-2">⚠️ Hinweise:</h4>
              <ul className="list-disc list-inside space-y-1 text-sm text-yellow-900">
                {result.cost_estimation.hinweise.map((hinweis, index) => (
                  <li key={index}>{hinweis}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Disclaimer */}
          <div className="text-xs text-gray-500 text-center">
            <p>{result.disclaimer}</p>
            <p className="mt-1">Generiert von: {result.generated_by}</p>
          </div>
        </div>
      )}
    </div>
  );
}
```

### 4. Page Component

Erstellen Sie `app/cost-estimate/page.tsx`:

```typescript
import CostEstimator from "@/components/CostEstimator";

export default function CostEstimatePage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 py-12 px-4">
      <CostEstimator />
    </main>
  );
}
```

---

## 🎯 Verwendung

### Schritt 1: Backend deployen
```bash
cd FastAPI_Classifier
# Neue Endpoint-Funktionalität hinzufügen
git add .
git commit -m "Add AI cost estimation endpoint"
git push origin main
```

### Schritt 2: Frontend implementieren
```bash
# In Ihrem Next.js Projekt
# 1. lib/api.ts erweitern
# 2. components/CostEstimator.tsx erstellen
# 3. app/cost-estimate/page.tsx erstellen
```

### Schritt 3: Testen
```bash
npm run dev
# Öffnen: http://localhost:3000/cost-estimate
```

---

## 💡 Features

✅ **KI-gestützte Berechnung**: Claude Sonnet 4.5 berücksichtigt Gebäudetyp, Standort, Fläche
✅ **DIN 276 konform**: Kostengruppen nach deutscher Norm
✅ **Intelligente Richtwerte**: Basierend auf Gebäudetyp und Bundesland
✅ **Detaillierte Beschreibungen**: Für jede Kostengruppe
✅ **€/m² Kennzahlen**: Für Vergleiche und Plausibilitätsprüfung
✅ **Schnell**: ~5-10 Sekunden (vs. 30-60 Sekunden für vollständigen Report)
✅ **JSON Response**: Einfach zu verarbeiten und anzuzeigen

---

## 🔧 Anpassungen

### Mehr Eingabeparameter hinzufügen:
```typescript
export interface CostEstimationRequest {
  // ... bestehende Felder
  energy_standard?: "GEG" | "Effizienzhaus40" | "Passivhaus";
  automation_level?: "basic" | "standard" | "premium";
  special_requirements?: string[];
}
```

### Excel-Export hinzufügen:
```typescript
const exportToExcel = (result: CostEstimationResponse) => {
  // Verwenden Sie eine Library wie xlsx oder exceljs
  // Um die Kosten als Excel-Tabelle zu exportieren
};
```

---

## ⚡ Performance-Tipps

- **Caching**: Speichern Sie Ergebnisse für gleiche Parameter
- **Streaming**: Verwenden Sie Server-Sent Events für Echtzeit-Updates
- **Batch-Requests**: Schätzen Sie mehrere Varianten auf einmal

---

Viel Erfolg mit der KI-gestützten Kostenschätzung! 🚀💰

