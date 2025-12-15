RealEstate_Analytics/
├── app/
│   └── real_estate_dashboard.py       # Streamlit app (interactive dashboard)
├── data/
│   ├── jvc_apartments_raw.csv         # Raw scraped data
│   ├── jvc_apartments_cleaned.csv     # Cleaned post-scraping
│   ├── jvc_apartments_processed.csv   # ML-ready dataset (preprocessing + feature engineering)
│   └── database.db                     # SQLite DB for dashboard & ML
├── models/
│   └── best_model.pkl                  # Saved ML model
├── notebooks/
│   ├── 01_web_scraping.ipynb
│   ├── 02_save_to_db.ipynb
│   ├── 03_data_preprocessing_feature_engineering.ipynb
│   └── 04_modelling_evaluation.ipynb
├── requirements.txt                    # Python libraries
├── architecture.md                     # Workflow diagram and explanation
└── README.md                            # Optional, project description & instructions
