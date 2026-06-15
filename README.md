# AI-Based Multimodal Healthcare Prediction System

This project is a rebuild-ready scaffold for an AI healthcare prediction system that combines multiple patient data modalities:

- Electronic Health Records (EHR): demographics, vitals, lab values, diagnoses, medications, and clinical notes.
- Genomics: variant features, disease markers, or learned genomic embeddings.
- Wearable sensors: time-series physiological signals such as heart rate, oxygen saturation, sleep, and activity.
- Medical images and reports: scans, X-rays, diagnostic report images, and clinical text.

The system is designed as a clinical decision-support framework for early disease-risk prediction. It does not replace clinicians; it helps flag high-risk patients earlier, explain which inputs contributed to the prediction, and support timely intervention.

## Key Features

- Modality-specific preprocessing and encoders.
- Attention-based multimodal fusion.
- Missing-modality masks for realistic hospital data.
- Multi-outcome risk prediction for tasks such as mortality, readmission, clinical event risk, and likely disease-risk category.
- Explainability hooks for feature-level and modality-level interpretation.
- UI dashboard for EHR, genomics, wearable sensor streams, and medical image/report inputs.
- FastAPI backend with a deterministic demo model for live review before a trained checkpoint is available.

## Project Structure

```text
project-root/
  config/              Model, training, path, and modality settings
  frontend/            React UI dashboard served as a static browser app
  backend/             FastAPI app used by the UI
  data/                Raw, processed, and sample data folders
  notebooks/           EDA, preprocessing, training, and results notebooks
  src/                 Application source code
  artifacts/           Trained models and fitted preprocessing assets
  reports/             Figures, tables, and final write-up
  docs/                Architecture, methodology, results, and UML notes
  tests/               Unit tests for preprocessing, fusion, models, and inference
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

For the UI demo, make sure FastAPI and Uvicorn are installed:

```powershell
pip install fastapi uvicorn
```

## Run Commands

Run the backend API:

```powershell
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Run the frontend in a second terminal:

```powershell
python -m http.server 5173 -d frontend
```

Open the UI:

```text
http://127.0.0.1:5173
```

Useful API endpoints:

```text
GET  http://127.0.0.1:8000/api/health
GET  http://127.0.0.1:8000/api/sample
POST http://127.0.0.1:8000/api/predict
```

Run a synthetic training smoke test:

```powershell
python -m src.main --mode train --demo
```

Run demo inference from a saved model:

```powershell
python -m src.main --mode infer --demo
```

Run evaluation once predictions and labels are available:

```powershell
python -m src.main --mode evaluate --predictions reports/tables/predictions.csv --labels reports/tables/labels.csv
```

Run tests:

```powershell
pytest
```

## UI Demo Flow

1. Open the Home page and click **Start Prediction**.
2. Fill the EHR form fields: age, gender, blood pressure, sugar level, heart rate, and medical history.
3. Click **Input sample data** to randomly fill all modalities from more than 10 demo patient profiles, or manually upload/fill each section.
4. Upload genomics `.csv` or `.txt`, or use **Sample genomics** only for that section.
5. Upload wearable `.csv` time-series data, or click **Simulate data** for real-time-like heart rate, steps, SpO2, and sleep values.
6. Upload an X-ray/scan image and a blood report image, then optionally type report findings.
7. Click **Run Prediction** to view risk level, disease-risk category, probability score, mortality risk, readmission risk, and cardiac/neuro event risk.
8. Review the Explainability and Dashboard pages for EHR feature importance, modality attention, wearable trends, disease-wise risk scores, risk score charts, and image heatmap preview.

## Backend UI Pipeline

```text
UI data input
  -> modality preprocessing
  -> EHR MLP-style encoder
  -> Genomics dense encoder
  -> Wearable GRU-style temporal encoder
  -> Image/report CNN-style encoder
  -> attention-based fusion
  -> prediction layer
  -> explainability response
  -> UI visualizations
```

The UI backend accepts incomplete patient records. Missing modalities receive a false modality mask and zero attention weight, while available modalities still produce a prediction.

## Example Output

The model outputs risk probabilities for configured outcomes:

```json
{
  "mortality": 0.18,
  "long_stay": 0.42,
  "readmission": 0.31,
  "clinical_event": 0.27
}
```

It can also expose modality attention weights, for example:

```json
{
  "ehr": 0.35,
  "genomics": 0.12,
  "wearable": 0.29,
  "image": 0.17,
  "text": 0.07
}
```

## Dataset Notes

This repository is dataset-agnostic. Hospital, benchmark, or synthetic datasets can be plugged in by adapting the loaders in `src/data_pipeline/`. The model is intentionally built to tolerate missing modalities through explicit masks and late fusion.

## Viva Points

- Real-time wearable simulation demonstrates streaming clinical signals.
- Explainable AI outputs improve doctor trust by showing EHR feature impact and modality attention.
- Multimodal fusion can improve accuracy because each encoder captures a different patient signal.
- The system handles incomplete patient records using modality masks.
- One-line explanation: "This is a UI-based AI healthcare system that integrates EHR, genomics, wearable data, and medical images to predict disease risk early using multimodal deep learning with explainable outputs."
