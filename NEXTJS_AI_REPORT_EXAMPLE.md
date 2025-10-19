# 🤖 AI Report Generator - Next.js Integration

## Komplettes Beispiel für AI Report Generation in Next.js

### 1. API Client erweitern

Fügen Sie zu `lib/api.ts` hinzu:

```typescript
// lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ReportRequest {
  project_name: string;
  location: string;
  project_type: "office" | "laboratory" | "hospital" | "school" | "residential";
  federal_state: string;
}

export interface ReportOptions {
  request: ReportRequest;
  room_book?: File;
  cost_estimate?: File;
  export_format: "docx" | "markdown";
}

/**
 * Generate AI-powered report using Claude Sonnet 4.5
 * Returns a Blob that can be downloaded
 */
export async function generateAIReport(options: ReportOptions): Promise<Blob> {
  const formData = new FormData();
  
  // Add request data as JSON string
  formData.append("request", JSON.stringify(options.request));
  
  // Add optional files
  if (options.room_book) {
    formData.append("room_book", options.room_book);
  }
  if (options.cost_estimate) {
    formData.append("cost_estimate", options.cost_estimate);
  }
  
  // Add export format
  formData.append("export_format", options.export_format);
  
  const response = await fetch(`${API_URL}/generate_report`, {
    method: "POST",
    body: formData,
    // Don't set Content-Type header - browser will set it with boundary
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `API Error: ${response.statusText}`);
  }
  
  return response.blob();
}

/**
 * Download a blob as a file
 */
export function downloadBlob(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}
```

### 2. React Component für Report Generation

Erstellen Sie `components/AIReportGenerator.tsx`:

```typescript
"use client";

import { useState } from "react";
import { generateAIReport, downloadBlob, type ReportRequest } from "@/lib/api";

const FEDERAL_STATES = [
  "Baden-Württemberg",
  "Bayern",
  "Berlin",
  "Brandenburg",
  "Bremen",
  "Hamburg",
  "Hessen",
  "Mecklenburg-Vorpommern",
  "Niedersachsen",
  "Nordrhein-Westfalen",
  "Rheinland-Pfalz",
  "Saarland",
  "Sachsen",
  "Sachsen-Anhalt",
  "Schleswig-Holstein",
  "Thüringen",
];

const PROJECT_TYPES = [
  { value: "office", label: "Bürogebäude" },
  { value: "laboratory", label: "Labor" },
  { value: "hospital", label: "Krankenhaus" },
  { value: "school", label: "Schule" },
  { value: "residential", label: "Wohngebäude" },
];

export default function AIReportGenerator() {
  const [formData, setFormData] = useState<ReportRequest>({
    project_name: "",
    location: "",
    project_type: "office",
    federal_state: "Bayern",
  });
  
  const [roomBook, setRoomBook] = useState<File | null>(null);
  const [costEstimate, setCostEstimate] = useState<File | null>(null);
  const [exportFormat, setExportFormat] = useState<"docx" | "markdown">("docx");
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      console.log("🚀 Generating AI report...");
      
      const blob = await generateAIReport({
        request: formData,
        room_book: roomBook || undefined,
        cost_estimate: costEstimate || undefined,
        export_format: exportFormat,
      });
      
      // Generate filename
      const extension = exportFormat === "docx" ? "docx" : "md";
      const sanitizedName = formData.project_name
        .replace(/[^a-zA-Z0-9äöüÄÖÜß]/g, "_")
        .substring(0, 50);
      const filename = `Erlaeuterungsbericht_${sanitizedName}.${extension}`;
      
      // Download file
      downloadBlob(blob, filename);
      
      setSuccess(true);
      console.log("✅ Report downloaded successfully!");
    } catch (err) {
      console.error("❌ Error:", err);
      setError(err instanceof Error ? err.message : "Ein Fehler ist aufgetreten");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">
          🤖 AI Report Generator
        </h2>
        <p className="text-gray-600">
          Powered by Claude Sonnet 4.5 - Generiert professionelle Erläuterungsberichte
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
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
            placeholder="z.B. Neubau Zentrale Muster GmbH"
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
            placeholder="z.B. München, Bayern"
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
                project_type: e.target.value as ReportRequest["project_type"],
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

        {/* Raumbuch Upload (Optional) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Raumbuch (Optional)
          </label>
          <input
            type="file"
            accept=".xlsx,.xls"
            onChange={(e) => setRoomBook(e.target.files?.[0] || null)}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          {roomBook && (
            <p className="mt-2 text-sm text-green-600">
              ✓ {roomBook.name} ({(roomBook.size / 1024).toFixed(1)} KB)
            </p>
          )}
        </div>

        {/* Kostenschätzung Upload (Optional) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Kostenschätzung (Optional)
          </label>
          <input
            type="file"
            accept=".xlsx,.xls"
            onChange={(e) => setCostEstimate(e.target.files?.[0] || null)}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          {costEstimate && (
            <p className="mt-2 text-sm text-green-600">
              ✓ {costEstimate.name} ({(costEstimate.size / 1024).toFixed(1)} KB)
            </p>
          )}
        </div>

        {/* Export Format */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Export Format
          </label>
          <div className="flex gap-4">
            <label className="flex items-center">
              <input
                type="radio"
                value="docx"
                checked={exportFormat === "docx"}
                onChange={(e) => setExportFormat(e.target.value as "docx")}
                className="mr-2"
              />
              <span className="text-gray-700">Word (DOCX)</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="markdown"
                checked={exportFormat === "markdown"}
                onChange={(e) => setExportFormat(e.target.value as "markdown")}
                className="mr-2"
              />
              <span className="text-gray-700">Markdown</span>
            </label>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-6 rounded-md hover:from-blue-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 transition-all font-medium text-lg shadow-md"
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
              KI generiert Bericht...
            </span>
          ) : (
            "🤖 Report mit AI generieren"
          )}
        </button>
      </form>

      {/* Error Message */}
      {error && (
        <div className="mt-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-md">
          <p className="font-medium">❌ Fehler:</p>
          <p>{error}</p>
        </div>
      )}

      {/* Success Message */}
      {success && (
        <div className="mt-6 p-4 bg-green-100 border border-green-400 text-green-700 rounded-md">
          <p className="font-medium">✅ Erfolgreich!</p>
          <p>Der Report wurde generiert und heruntergeladen.</p>
        </div>
      )}

      {/* Info Box */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
        <p className="text-sm text-blue-800">
          <strong>ℹ️ Hinweis:</strong> Die Generierung dauert ca. 30-60 Sekunden,
          da Claude AI jeden Abschnitt intelligent erstellt.
        </p>
      </div>
    </div>
  );
}
```

### 3. Page Component (App Router)

Erstellen Sie `app/ai-report/page.tsx`:

```typescript
import AIReportGenerator from "@/components/AIReportGenerator";

export default function AIReportPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-12 px-4">
      <div className="container mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            AI-Powered Report Generator
          </h1>
          <p className="text-xl text-gray-600">
            Generiert professionelle Erläuterungsberichte mit Claude Sonnet 4.5
          </p>
        </div>
        
        <AIReportGenerator />
        
        {/* Feature List */}
        <div className="mt-12 max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-6">Features</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-3xl mb-3">🤖</div>
              <h3 className="font-bold mb-2">AI-Powered</h3>
              <p className="text-sm text-gray-600">
                Claude Sonnet 4.5 generiert intelligente, kontextbezogene Inhalte
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-3xl mb-3">📋</div>
              <h3 className="font-bold mb-2">HOAI-Konform</h3>
              <p className="text-sm text-gray-600">
                Erläuterungsberichte nach Leistungsphase 2 (HOAI)
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-3xl mb-3">⚡</div>
              <h3 className="font-bold mb-2">Schnell</h3>
              <p className="text-sm text-gray-600">
                Kompletter Bericht in 30-60 Sekunden statt Stunden
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
```

### 4. Alternative: Server Action Ansatz

Für Next.js 14+ mit Server Actions:

```typescript
// app/actions/report.ts
"use server";

export async function generateReport(formData: FormData) {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  
  try {
    const response = await fetch(`${API_URL}/generate_report`, {
      method: "POST",
      body: formData,
    });
    
    if (!response.ok) {
      const error = await response.json();
      return { success: false, error: error.detail };
    }
    
    const blob = await response.blob();
    const arrayBuffer = await blob.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    
    return {
      success: true,
      data: buffer.toString("base64"),
      contentType: response.headers.get("content-type") || "application/octet-stream",
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }
}
```

### 5. TypeScript Types (Optional aber empfohlen)

Erstellen Sie `types/report.ts`:

```typescript
export type ProjectType = "office" | "laboratory" | "hospital" | "school" | "residential";

export type ExportFormat = "docx" | "markdown";

export interface ReportRequest {
  project_name: string;
  location: string;
  project_type: ProjectType;
  federal_state: string;
}

export interface ReportGenerationOptions {
  request: ReportRequest;
  room_book?: File;
  cost_estimate?: File;
  export_format: ExportFormat;
}

export const FEDERAL_STATES = [
  "Baden-Württemberg",
  "Bayern",
  "Berlin",
  "Brandenburg",
  "Bremen",
  "Hamburg",
  "Hessen",
  "Mecklenburg-Vorpommern",
  "Niedersachsen",
  "Nordrhein-Westfalen",
  "Rheinland-Pfalz",
  "Saarland",
  "Sachsen",
  "Sachsen-Anhalt",
  "Schleswig-Holstein",
  "Thüringen",
] as const;

export const PROJECT_TYPE_LABELS: Record<ProjectType, string> = {
  office: "Bürogebäude",
  laboratory: "Labor",
  hospital: "Krankenhaus",
  school: "Schule",
  residential: "Wohngebäude",
};
```

### 6. Environment Variables

In `.env.local`:

```bash
NEXT_PUBLIC_API_URL=https://house-type-predictor-fastapi-production.up.railway.app
```

In Vercel/Netlify/Railway (Next.js Projekt):

```bash
NEXT_PUBLIC_API_URL=https://ihre-fastapi.railway.app
```

### 7. Testing

```bash
npm run dev
```

Dann öffnen Sie: `http://localhost:3000/ai-report`

## 🎯 Verwendung:

1. Füllen Sie das Formular aus
2. Optional: Laden Sie Excel-Dateien hoch
3. Wählen Sie das Export-Format
4. Klicken Sie "Report mit AI generieren"
5. Download startet automatisch nach ~30-60 Sekunden

## 📝 Tipps:

- **Excel-Format für Raumbuch**: Spalten wie `room_type`, `area_m2`
- **Excel-Format für Kosten**: Kostengruppen und Beträge
- **DOCX vs Markdown**: DOCX für professionelle Dokumente, Markdown für Vorschau
- **Generation dauert**: 30-60 Sekunden (Claude generiert 8+ Abschnitte)
- **Kosten**: ~$0.30-0.50 pro Report (Claude API Kosten)

## ⚠️ Error Handling:

Häufige Fehler und Lösungen:

1. **"ANTHROPIC_API_KEY not found"**
   - API Key in Railway Environment Variables setzen
   
2. **"CORS Error"**
   - Prüfen Sie `allow_origins` in FastAPI
   
3. **"Network Error"**
   - Prüfen Sie `NEXT_PUBLIC_API_URL`
   
4. **"File too large"**
   - FastAPI default: 2MB - kann in `main.py` erhöht werden

## 🚀 Deployment:

Beide Apps müssen deployed sein:
- **FastAPI Backend**: Railway (mit ANTHROPIC_API_KEY)
- **Next.js Frontend**: Vercel/Netlify/Railway

Beide kommunizieren über die API URL!

