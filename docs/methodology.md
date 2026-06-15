# Methodology

## Data Ingestion

Each modality has its own loader under `src/data_pipeline/`. Loaders keep raw inputs separate from processed outputs.

## Preprocessing

- EHR: imputation, numeric scaling, categorical encoding.
- Genomics: normalization, optional feature selection, embedding preparation.
- Wearables: resampling, smoothing, padding or truncation into fixed-length sequences.
- Images: resizing, normalization, and optional augmentation.
- Text: tokenization and conversion to model-ready token IDs or embeddings.

## Feature Extraction

Each modality is encoded independently into a shared embedding dimension. This keeps the model modular and easier to debug.

## Fusion

The attention fusion layer learns modality weights for each patient. It can emphasize the most informative modality for a specific case and ignore missing modalities through masks.

## Prediction

The prediction head produces risk scores for configured outcomes such as mortality, long stay, readmission, and clinical event risk.
