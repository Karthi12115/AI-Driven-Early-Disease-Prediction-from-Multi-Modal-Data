# Architecture

The system follows a high-level multimodal pipeline: ingestion, modality-specific preprocessing, feature extraction, attention-based fusion, prediction, and explanation.

```mermaid
flowchart LR
  EHR["EHR data"] --> EHRP["EHR preprocessing"] --> EHRE["EHR encoder"]
  GEN["Genomics"] --> GENP["Genomics preprocessing"] --> GENE["Genomics encoder"]
  WEA["Wearables"] --> WEAP["Sequence preprocessing"] --> WEAE["Temporal encoder"]
  IMG["Images and reports"] --> IMGP["Image preprocessing"] --> IMGE["Vision encoder"]
  TXT["Clinical notes"] --> TXTP["Text preprocessing"] --> TXTE["Text encoder"]

  EHRE --> FUS["Attention fusion"]
  GENE --> FUS
  WEAE --> FUS
  IMGE --> FUS
  TXTE --> FUS

  FUS --> PRED["Risk prediction head"]
  FUS --> XAI["Modality explanation"]
  PRED --> OUT["Risk probabilities"]
  XAI --> CLIN["Clinician-facing insights"]
```

## Missing Data Strategy

Every patient record includes a modality mask. The fusion layer uses this mask to ignore missing branches instead of assuming all inputs are present. This supports real clinical data, where patients may lack genomics, wearable streams, imaging, or free-text notes.
