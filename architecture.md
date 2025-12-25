# Real Estate Analytics Dashboard - Architecture

## Overview
This project is a **Streamlit-based web dashboard** for analyzing and predicting apartment rents in Jumeirah Village Circle (JVC), Dubai. It integrates **database queries, data visualizations, and a machine learning model** to provide insights for tenants, investors, and property managers.

## Project Components

### 1. Database
- **SQLite database (`database.db`)** contains apartment listings with fields like:
  - `location`, `building`, `bedrooms`, `bathrooms`, `area_clean`, `price_yearly_aed`
- Stores historical and current listings for analysis.

### 2. Streamlit App
- **Tabs:**
  1. **Market Overview**
     - Filters for bedrooms, rent, area, and building
     - Metrics (KPIs): average rent, average size, price per sqft
     - Charts: histograms, scatter plots, pie charts, bar charts
     - Market insights and value analysis
  2. **Rent Predictor**
     - User inputs: bedrooms, bathrooms, area, building, district
     - Uses trained ML model to estimate fair annual rent
     - Compares predicted rent with overall JVC average

### 3. Feature Engineering
- **feature_builder.py** converts user input into model-ready features:
  - One-hot encoding for categorical variables (building, district)
  - Derived features: `area_per_bedroom`, `bathrooms_per_bedroom`, `log_area`

### 4. Machine Learning Model
- Trained with historical apartment data
- Predicts **annual rent** based on features
- Saved as `best_model.pkl` and loaded in Streamlit

## Data Flow

```
User Input (Filters / Predictor)
│
▼
SQLite DB (Load Listings)
│
▼
DataFrame + Feature Engineering
│
├─► Visualizations (Plotly charts) ─► Display in Market Overview
│
└─► ML Model Prediction ─► Display in Rent Predictor
```


## Notes
- All dependencies are in `requirements.txt` (runtime) and `requirements-dev.txt` (development)
- App is fully self-contained and requires only Python + pip to run
- Streamlit caching (`@st.cache_data`, `@st.cache_resource`) is used to optimize performance
