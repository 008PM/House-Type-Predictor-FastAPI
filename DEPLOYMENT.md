# 🚀 Railway Deployment Anleitung

## Voraussetzungen
- GitHub Account
- Railway Account (https://railway.app)
- Dieses Repository auf GitHub gepusht

## Schritt 1: Railway Projekt erstellen

1. Gehen Sie zu [Railway](https://railway.app) und melden Sie sich an
2. Klicken Sie auf **"New Project"**
3. Wählen Sie **"Deploy from GitHub repo"**
4. Autorisieren Sie Railway für Ihren GitHub Account
5. Wählen Sie das **House-Type-Predictor-FastAPI** Repository

## Schritt 2: Deployment konfigurieren

Railway erkennt automatisch:
- Die `railway.toml` Konfiguration
- Die `requirements.txt` für Python-Dependencies
- **Railpack** analysiert automatisch Ihr Projekt

### Build-Methode: Railpack (Nachfolger von Nixpacks)
Railpack ist der moderne Zero-Config Builder von Railway mit:
- ✅ Automatischer Spracherkennung
- ✅ Besserem Caching und schnelleren Builds
- ✅ Kleineren Container-Images
- ✅ Granularer Versionskontrolle

### Wichtige Einstellungen:
- **Builder**: Railpack (automatisch)
- **Root Directory**: `/` (Projekt-Root)
- **Port**: Railway stellt automatisch `$PORT` bereit
- **Python Version**: Wird automatisch erkannt
- **Dependencies**: Aus `requirements.txt` im Root

## Schritt 3: Deployment starten

1. Railway startet automatisch das Deployment
2. Railpack analysiert Ihr Projekt und erstellt den Build (~2-4 Minuten)
3. Nach erfolgreichem Deployment erhalten Sie eine URL wie:
   ```
   https://ihr-projekt.railway.app
   ```

### Railpack aktivieren (falls nötig)

Railpack sollte automatisch verwendet werden. Falls nicht:
1. Gehen Sie zu Ihrem Railway Projekt
2. Klicken Sie auf **Settings**
3. Unter **Builder** wählen Sie **Railpack**
4. Speichern und neu deployen

## Schritt 4: API testen

### Health Check:
```bash
curl https://ihr-projekt.railway.app/
```

### Swagger UI:
Öffnen Sie im Browser:
```
https://ihr-projekt.railway.app/docs
```

### Test Prediction:
```bash
curl -X POST https://ihr-projekt.railway.app/predict \
  -H "Content-Type: application/json" \
  -d '{
    "volume_m3": 50.5,
    "area_m2": 25.0,
    "total_heating_load_kw": 3.5
  }'
```

## Schritt 5: Umgebungsvariablen (Optional)

Falls Sie CORS auf spezifische Origins beschränken möchten:

1. Gehen Sie zu Ihrem Railway Projekt
2. Klicken Sie auf **"Variables"**
3. Fügen Sie hinzu:
   ```
   ALLOWED_ORIGINS=https://ihre-nextjs-app.vercel.app
   ```
4. Passen Sie `app/main.py` an, um diese Variable zu nutzen

## Troubleshooting

### Build schlägt fehl
- ✅ **Gelöst**: Projekt verwendet jetzt **Railpack** (Nachfolger von Nixpacks)
- Railpack erkennt Python automatisch über `requirements.txt` im Root
- Überprüfen Sie die Logs in Railway Dashboard

### "Module not found" Fehler
- ✅ **Gelöst**: `__init__.py` Dateien wurden hinzugefügt
- Railpack installiert alle Dependencies aus `requirements.txt`
- Stellen Sie sicher, dass `FastAPI_Classifier/__init__.py` existiert

### Railpack wird nicht verwendet
- Gehen Sie zu Railway Project Settings
- Wählen Sie unter "Builder" explizit **Railpack**
- Triggern Sie ein neues Deployment

### API nicht erreichbar
- Überprüfen Sie, ob der Health Check (`/`) funktioniert
- Prüfen Sie die Railway Logs auf Fehler
- Warten Sie ~2-3 Minuten nach Deployment

### CORS-Fehler im Frontend
- Stellen Sie sicher, dass CORS in `main.py` konfiguriert ist
- Überprüfen Sie die `allow_origins` Einstellung
- Testen Sie mit Browser DevTools Console

## Kosten
Railway bietet:
- **$5 Guthaben pro Monat** kostenlos
- Danach: Pay-as-you-go
- Kleine APIs wie diese kosten typischerweise < $5/Monat

## Auto-Deployment
Railway aktiviert automatisch:
- ✅ Deployment bei jedem `git push` zum `main` Branch
- ✅ Preview-Deployments für Pull Requests (optional)
- ✅ Automatische Health Checks

---

## Next.js Integration

Nach dem Deployment notieren Sie sich die Railway URL und verwenden Sie diese in Ihrem Next.js Frontend:

```typescript
const API_URL = "https://ihr-projekt.railway.app";
```

Siehe `NEXTJS_EXAMPLE.md` für vollständigen Frontend-Code.


