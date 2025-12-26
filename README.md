# JVC Real Estate Analytics Dashboard

A **data-driven interactive dashboard** to explore and predict apartment rental prices in **Jumeirah Village Circle (JVC), Dubai**.  

This project combines **web scraping, data cleaning, feature engineering, machine learning, and interactive dashboards** to provide actionable insights for tenants, investors, and property managers.

Built with **Python, Streamlit, SQLite, Plotly, scikit-learn, XGBoost, LightGBM, and Joblib**.

---

## Project Overview

This project is divided into four main stages:

1. **Web Scraping & Data Collection**  
   - Scrape apartment listings from Bayut.com for JVC
   - Backup scraped pages to CSV
   - Extract key listing info: title, price, property type, bedrooms, bathrooms, area, location, and URL
   - Tools used: `selenium`, `BeautifulSoup4`, `pandas`, `time`, `random`

2. **Data Cleaning & Storage**  
   - Cleaned and normalized raw scraped data
   - Remove duplicates, fix formats, handle missing values
   - Save data to **CSV** and **SQLite database** (`database.db`)
   - Query database to verify insertion
   - Tools used: `pandas`, `sqlite3`

3. **Feature Engineering & Preprocessing**  
   - Target: `price_yearly_aed` (annual rent)
   - Create derived features:
     - `area_per_bedroom`
     - `bathrooms_per_bedroom`
     - `log_area`
     - `log_price` (for ML)
   - Extract building, district, and community from location
   - Handle high-cardinality categorical features:
     - Keep top N buildings, group rest as "Other"
   - One-hot encode categorical features (`property_type`, `building_grouped`, `district`)
   - Save processed CSV for ML (`jvc_apartments_ml.csv`) and update dashboard database
   - Tools used: `pandas`, `numpy`, `sqlite3`

4. **Machine Learning & Model Evaluation**  
   - Regression problem: predict annual rent
   - Models trained and compared:
     - Baseline
     - Linear Regression
     - Decision Tree Regressor
     - Random Forest Regressor
     - XGBoost Regressor
     - LightGBM Regressor
   - Metrics used: **MAE**, **RMSE**, **R²**
   - Hyperparameter tuning using `RandomizedSearchCV` (Random Forest)
   - Save best-performing model (`best_model.pkl`) for dashboard use
   - Tools used: `scikit-learn`, `xgboost`, `lightgbm`, `joblib`, `pandas`, `numpy`

5. **Interactive Dashboard**  
   - Built with **Streamlit**
   - **Market Overview Tab**:
     - Filter by bedrooms, rent, size, building
     - KPIs: active listings, average rent, unit size, price per sqft
     - Interactive plots: histogram, scatter, pie, bar
     - Market insights & best-value buildings
   - **Rent Price Predictor Tab**:
     - Input unit characteristics
     - Predict annual rent with ML model
     - Compare prediction to market average
   - Tools used: `streamlit`, `plotly`, `pandas`, `joblib`, `sqlite3`

---

## Tools & Technologies Used

- **Python 3.11+** – main programming language
- **Streamlit** – dashboard & UI
- **SQLite** – database for apartment listings
- **Pandas & NumPy** – data manipulation
- **Plotly** – interactive visualizations
- **scikit-learn** – ML models and evaluation
- **XGBoost & LightGBM** – advanced regression models
- **Joblib** – save/load trained models
- **BeautifulSoup4 & Selenium** – web scraping
- **Jupyter Notebooks** – EDA, data pipeline, and ML development
- **Git & GitHub** – version control

---

## Project Structure

RealEstate_Analytics/
- **app/**
  - `real_estate_dashboard.py` – main Streamlit app  
  - `feature_builder.py` – converts user input to ML-ready features  
- **data/**
  - `database.db` – SQLite database  
  - `jvc_apartments_raw.csv` – raw scraped data  
  - `jvc_apartments_cleaned.csv` – cleaned dataset  
  - `jvc_apartments_ml.csv` – dataset for ML training  
  - `backups/` – backup CSVs of scraped pages  
- **models/**
  - `best_model.pkl` – saved ML model for predictions  
- **notebooks/**
  - `01_web_scraping.ipynb` – scrape apartment listings  
  - `02_saving_data_into_db.ipynb` – save data to SQLite  
  - `03_data_preprocessing_feature_engineering.ipynb` – feature engineering  
  - `04_modelling_evaluation.ipynb` – model training, tuning, evaluation  
- `requirements.txt` – runtime dependencies  
- `requirements-dev.txt` – development dependencies  
- `architecture.md` – project architecture & pipeline  
- `README.md` – this file  

---

## Key Features

### Market Overview
- Filter apartments by bedrooms, rent, size, and building
- View interactive visualizations:
  - Rent distribution by bedrooms
  - Rent vs size scatter plot
  - Listing distribution pie chart
  - Best-value buildings bar chart
- Dynamic market insights

### Rent Price Predictor
- Input apartment details
- Predict annual rent using ML model
- Compare prediction to market average for value assessment

---

## Demo

- **Demonstration of the Streamlit dashboard:** (https://youtu.be/4OoVJMgdW94)

---

## Setup & Installation

1. Clone the repository:
```bash
git clone https://github.com/AymanBerri/RealEstate_Analytics.git
cd RealEstate_Analytics
```
2. Create and activate a virtual environment:

- Windows:
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```         
    
- macOS/Linux:

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```


3. Install dependencies:
```bash
pip install -r requirements.txt
```


4. Run the app:
```bash
streamlit run app/real_estate_dashboard.py
```

## Target Users

- **Tenants:** Fair rental range insights  
- **Investors:** Identify value opportunities  
- **Property Managers:** Benchmark assets  
- **Data Analysts:** Extend the pipeline to other communities  

## Skills & Competencies Demonstrated

- Web scraping & automation using Selenium and BeautifulSoup  
- Data cleaning & manipulation with Pandas  
- Database management with SQLite  
- Feature engineering & preprocessing for ML  
- Regression modeling & evaluation (Random Forest, XGBoost, LightGBM, Linear Regression)  
- Hyperparameter tuning & model selection  
- Interactive dashboard development with Streamlit and Plotly  
- Version control & project organization  

## Architecture

See [architecture.md](architecture.md) for a visual and textual breakdown of the **data pipeline**, **dashboard flow**, and **ML integration**.

