# app.py - Real Estate Analytics Dashboard (Hugging Face Compatible)
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
import pickle
from io import BytesIO
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="JVC Real Estate Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM FEATURE BUILDER (from your feature_builder.py)
# ============================================================================
def build_features(user_input, model_columns):
    """
    Convert user input into ML-ready features
    Identical to your original feature_builder.py
    """
    # Create empty DataFrame with all model columns
    X = pd.DataFrame(0, index=[0], columns=model_columns)
    
    # Numerical features
    X["bedrooms_clean"] = user_input["bedrooms"]
    X["bathrooms_clean"] = user_input["bathrooms"]
    X["area_clean"] = user_input["area"]
    X["area_per_bedroom"] = user_input["area"] / max(user_input["bedrooms"], 1)
    X["bathrooms_per_bedroom"] = user_input["bathrooms"] / max(user_input["bedrooms"], 1)
    X["log_area"] = np.log(user_input["area"])
    
    # One-hot encoding for categorical features
    building = user_input.get("building", "").lower().replace(" ", "_").replace("-", "_")
    building_col = f"building_grouped_{building}"
    
    if building_col in X.columns:
        X[building_col] = 1
    elif "building_grouped_other" in X.columns:
        X["building_grouped_other"] = 1
    
    district_col = "district_jvc"
    if district_col in X.columns:
        X[district_col] = 1
    
    property_col = "property_type_apartment"
    if property_col in X.columns:
        X[property_col] = 1
    
    return X

# ============================================================================
# SAMPLE DATA GENERATOR (replaces SQLite database)
# ============================================================================
@st.cache_data
def generate_realistic_data():
    """
    Generate realistic JVC apartment data matching your schema
    This replaces the SQLite database for deployment
    """
    np.random.seed(42)
    n_samples = 250
    
    # Building names from your JVC data
    buildings = [
        'Al Khail', 'Mirage', 'Park View', 'JVC Towers', 'Green Community',
        'La Vie', 'Maple', 'Saba', 'Elan', 'Meydan', 'Platinum', 'Viva'
    ]
    
    # Generate realistic data
    data = pd.DataFrame({
        'id': range(1, n_samples + 1),
        'bedrooms_clean': np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.25, 0.35, 0.25, 0.10, 0.05]),
        'bathrooms_clean': np.clip(np.random.choice([1, 2, 3, 4], n_samples, p=[0.2, 0.5, 0.25, 0.05]), 1, 4),
        'area_clean': np.random.randint(450, 3200, n_samples),
        'building': np.random.choice(buildings, n_samples),
        'location': np.random.choice([
            'Al Khail, JVC, Dubai', 'Mirage, JVC, Dubai', 'Park View, JVC, Dubai',
            'JVC Towers, JVC, Dubai', 'Green Community, JVC, Dubai'
        ], n_samples),
        'property_type': 'Apartment',
        'district': 'JVC'
    })
    
    # Realistic price calculation based on Dubai JVC market
    base_price = 35000
    data['price_yearly_aed'] = (
        base_price +
        data['area_clean'] * 42 +  # ~42 AED per sqft
        data['bedrooms_clean'] * 16500 +
        data['bathrooms_clean'] * 7500
    )
    
    # Add building premiums
    building_premiums = {
        'Al Khail': 12000, 'Mirage': 15000, 'Park View': 8000,
        'JVC Towers': 18000, 'Green Community': 20000,
        'La Vie': 10000, 'Maple': 9000, 'Saba': 11000,
        'Elan': 13000, 'Meydan': 16000, 'Platinum': 22000, 'Viva': 9500
    }
    
    for building_name, premium in building_premiums.items():
        mask = data['building'] == building_name
        data.loc[mask, 'price_yearly_aed'] += premium
    
    # Add some randomness and ensure realistic range
    data['price_yearly_aed'] = data['price_yearly_aed'] + np.random.normal(0, 8000, n_samples)
    data['price_yearly_aed'] = data['price_yearly_aed'].clip(40000, 250000)
    
    # Calculate derived metrics
    data['price_per_sqft'] = data['price_yearly_aed'] / data['area_clean']
    data['price_per_bedroom'] = data['price_yearly_aed'] / data['bedrooms_clean']
    
    # Add "building" column for micro-market analysis (as in your original code)
    data['building_micro'] = data['location'].str.split(",").str[0].str.strip()
    
    return data

# ============================================================================
# ML MODEL LOADER (with fallback)
# ============================================================================
@st.cache_resource
def load_prediction_model():
    """
    Try to load your actual model, otherwise create a realistic one
    """
    try:
        # Try to load compressed model if uploaded
        model = joblib.load("model_light.pkl")
        st.success("✅ Loaded trained ML model")
        
        # Ensure it has feature names
        if not hasattr(model, 'feature_names_in_'):
            # Set expected feature names based on your original model
            model.feature_names_in_ = [
                'bedrooms_clean', 'bathrooms_clean', 'area_clean',
                'area_per_bedroom', 'bathrooms_per_bedroom', 'log_area',
                'building_grouped_al_khail', 'building_grouped_mirage',
                'building_grouped_park_view', 'building_grouped_jvc_towers',
                'building_grouped_green_community', 'building_grouped_la_vie',
                'building_grouped_maple', 'building_grouped_saba',
                'building_grouped_elan', 'building_grouped_meydan',
                'building_grouped_platinum', 'building_grouped_viva',
                'district_jvc', 'property_type_apartment'
            ]
        
        return model
    
    except FileNotFoundError:
        # Create a realistic ML model based on your data
        st.info("📊 Using simulated ML model (trained on realistic data)")
        
        from sklearn.ensemble import RandomForestRegressor
        
        # Generate data for training
        train_data = generate_realistic_data()
        
        # Prepare features (simplified version)
        X_train = train_data[['bedrooms_clean', 'bathrooms_clean', 'area_clean']].copy()
        X_train['area_per_bedroom'] = X_train['area_clean'] / X_train['bedrooms_clean']
        X_train['bathrooms_per_bedroom'] = X_train['bathrooms_clean'] / X_train['bedrooms_clean']
        X_train['log_area'] = np.log(X_train['area_clean'])
        
        y_train = train_data['price_yearly_aed']
        
        # Train model
        model = RandomForestRegressor(
            n_estimators=50,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        # Add feature names to match your original
        model.feature_names_in_ = list(X_train.columns)
        
        return model

# ============================================================================
# LOAD DATA AND MODEL
# ============================================================================
df = generate_realistic_data()
model = load_prediction_model()
model_columns = list(model.feature_names_in_)

# ============================================================================
# STREAMLIT APP - MARKET OVERVIEW TAB
# ============================================================================
st.title("🏢 JVC Real Estate Analytics Dashboard")
st.markdown("""
**Data-driven insights into Dubai's Jumeirah Village Circle apartment rental market.**  
Explore pricing trends, compare buildings, and predict rental values.
""")

# Create tabs like your original app
tab1, tab2 = st.tabs(["📊 Market Overview", "🔮 Rent Predictor"])

with tab1:
    # SIDEBAR FILTERS (identical to your original UI)
    st.sidebar.header("🎯 Market Filters")
    
    # Bedrooms filter
    bedroom_options = sorted(df["bedrooms_clean"].unique())
    selected_bedrooms = st.sidebar.multiselect(
        "Bedrooms",
        options=bedroom_options,
        default=bedroom_options,
        help="Filter by number of bedrooms"
    )
    
    # Price range slider
    min_price, max_price = st.sidebar.slider(
        "Annual Rent Range (AED)",
        min_value=int(df["price_yearly_aed"].min()),
        max_value=int(df["price_yearly_aed"].max()),
        value=(50000, 180000),
        step=5000,
        help="Adjust price range"
    )
    
    # Area range slider
    min_area, max_area = st.sidebar.slider(
        "Apartment Size (sqft)",
        min_value=int(df["area_clean"].min()),
        max_value=int(df["area_clean"].max()),
        value=(500, 2500),
        step=50,
        help="Filter by apartment area"
    )
    
    # Building filter
    top_buildings = df["building"].value_counts().head(10).index.tolist()
    selected_buildings = st.sidebar.multiselect(
        "Building / Community",
        options=top_buildings,
        default=top_buildings[:5],
        help="Select specific buildings"
    )
    
    # Apply filters
    filtered_df = df.copy()
    if selected_bedrooms:
        filtered_df = filtered_df[filtered_df["bedrooms_clean"].isin(selected_bedrooms)]
    
    filtered_df = filtered_df[
        (filtered_df["price_yearly_aed"] >= min_price) &
        (filtered_df["price_yearly_aed"] <= max_price) &
        (filtered_df["area_clean"] >= min_area) &
        (filtered_df["area_clean"] <= max_area)
    ]
    
    if selected_buildings:
        filtered_df = filtered_df[filtered_df["building"].isin(selected_buildings)]
    
    # MARKET METRICS (KPIs)
    st.subheader("Market Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Active Listings",
            value=len(filtered_df),
            delta=f"{len(filtered_df) - 100 if len(filtered_df) > 100 else 0}",
            delta_color="normal"
        )
    
    with col2:
        avg_price = filtered_df["price_yearly_aed"].mean()
        st.metric(
            label="Avg. Annual Rent",
            value=f"{avg_price:,.0f} AED"
        )
    
    with col3:
        avg_size = filtered_df["area_clean"].mean()
        st.metric(
            label="Avg. Unit Size",
            value=f"{avg_size:,.0f} sqft"
        )
    
    with col4:
        avg_ppsft = filtered_df["price_per_sqft"].mean()
        st.metric(
            label="Avg. Price/sqft",
            value=f"{avg_ppsft:,.1f} AED"
        )
    
    # VISUALIZATIONS
    if len(filtered_df) > 0:
        # 1. Price Distribution Histogram
        st.subheader("Price Distribution")
        fig_price = px.histogram(
            filtered_df,
            x="price_yearly_aed",
            nbins=25,
            color="bedrooms_clean",
            color_discrete_sequence=px.colors.qualitative.Set2,
            title="Distribution of Annual Rents",
            labels={"price_yearly_aed": "Annual Rent (AED)", "count": "Number of Listings"}
        )
        fig_price.update_layout(bargap=0.1)
        st.plotly_chart(fig_price, use_container_width=True)
        
        # 2. Average Rent by Bedroom Count
        st.subheader("Pricing by Unit Type")
        avg_by_bedroom = filtered_df.groupby("bedrooms_clean")["price_yearly_aed"].mean().reset_index()
        
        fig_bedroom = px.bar(
            avg_by_bedroom,
            x="bedrooms_clean",
            y="price_yearly_aed",
            text_auto=".0f",
            title="Average Annual Rent by Bedroom Count",
            labels={"bedrooms_clean": "Bedrooms", "price_yearly_aed": "Average Rent (AED)"},
            color="bedrooms_clean",
            color_continuous_scale=px.colors.sequential.Viridis
        )
        fig_bedroom.update_traces(texttemplate='%{text:,} AED', textposition='outside')
        st.plotly_chart(fig_bedroom, use_container_width=True)
        
        # 3. Rent vs Size Scatter Plot
        st.subheader("Rent vs Apartment Size")
        fig_scatter = px.scatter(
            filtered_df,
            x="area_clean",
            y="price_yearly_aed",
            color="bedrooms_clean",
            size="price_per_sqft",
            hover_data=["building", "location"],
            title="Relationship Between Size and Rent",
            labels={
                "area_clean": "Apartment Size (sqft)",
                "price_yearly_aed": "Annual Rent (AED)",
                "bedrooms_clean": "Bedrooms"
            },
            trendline="ols",
            trendline_color_override="red"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # 4. Building Analysis
        st.subheader("Building Analysis")
        building_analysis = filtered_df.groupby("building").agg({
            "price_yearly_aed": "mean",
            "price_per_sqft": "mean",
            "id": "count"
        }).round(0).sort_values("price_per_sqft", ascending=True)
        
        building_analysis.columns = ["Avg Rent (AED)", "Price/sqft (AED)", "Listings"]
        
        fig_building = px.bar(
            building_analysis.reset_index(),
            x="Price/sqft (AED)",
            y="building",
            orientation="h",
            title="Value Analysis by Building (Lower = Better Value)",
            labels={"building": "Building", "value": "Price per sqft (AED)"},
            color="Listings",
            color_continuous_scale=px.colors.sequential.Plasma
        )
        st.plotly_chart(fig_building, use_container_width=True)
        
        # 5. Top Value Buildings
        st.subheader("💎 Best Value Buildings")
        top_value = building_analysis.nsmallest(5, "Price/sqft (AED)")
        
        for idx, (building_name, row) in enumerate(top_value.iterrows(), 1):
            with st.container():
                cols = st.columns([2, 1, 1, 1])
                cols[0].markdown(f"**{idx}. {building_name}**")
                cols[1].metric("Rent", f"{row['Avg Rent (AED)']:,.0f} AED")
                cols[2].metric("Price/sqft", f"{row['Price/sqft (AED)']:,.0f} AED")
                cols[3].metric("Listings", row['Listings'])
                st.divider()
        
        # 6. Data Table
        with st.expander("📋 View Filtered Data"):
            display_cols = ['building', 'bedrooms_clean', 'bathrooms_clean', 
                          'area_clean', 'price_yearly_aed', 'price_per_sqft']
            st.dataframe(
                filtered_df[display_cols].rename(columns={
                    'building': 'Building',
                    'bedrooms_clean': 'Bedrooms',
                    'bathrooms_clean': 'Bathrooms',
                    'area_clean': 'Area (sqft)',
                    'price_yearly_aed': 'Annual Rent (AED)',
                    'price_per_sqft': 'Price/sqft (AED)'
                }).sort_values('Annual Rent (AED)'),
                use_container_width=True,
                height=400
            )
    
    else:
        st.warning("⚠️ No listings match your filters. Try adjusting the criteria.")

# ============================================================================
# RENT PREDICTOR TAB
# ============================================================================
with tab2:
    st.header("🏠 Apartment Rent Predictor")
    st.markdown("""
    Estimate the fair market rent for a property based on its characteristics.  
    *Powered by machine learning trained on JVC market data.*
    """)
    
    # Input form in two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Property Details")
        bedrooms = st.selectbox(
            "Bedrooms",
            options=[1, 2, 3, 4, 5],
            index=1,
            help="Number of bedrooms"
        )
        
        bathrooms = st.selectbox(
            "Bathrooms",
            options=[1, 2, 3, 4],
            index=1,
            help="Number of bathrooms"
        )
        
        area = st.number_input(
            "Apartment Size (sqft)",
            min_value=300,
            max_value=5000,
            value=1200,
            step=50,
            help="Total area in square feet"
        )
    
    with col2:
        st.subheader("Location Details")
        
        building_options = [
            'Al Khail', 'Mirage', 'Park View', 'JVC Towers', 'Green Community',
            'La Vie', 'Maple', 'Saba', 'Elan', 'Meydan', 'Platinum', 'Viva'
        ]
        
        building = st.selectbox(
            "Building / Community",
            options=building_options,
            index=0,
            help="Select the building or community"
        )
        
        district = st.selectbox(
            "District",
            options=["JVC"],
            disabled=True,
            help="Currently focused on Jumeirah Village Circle"
        )
    
    # PREDICTION BUTTON
    predict_col1, predict_col2, predict_col3 = st.columns([1, 2, 1])
    with predict_col2:
        predict_button = st.button(
            "🚀 Predict Rent Price",
            type="primary",
            use_container_width=True
        )
    
    if predict_button:
        with st.spinner("Analyzing property features..."):
            # Prepare user input
            user_input = {
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "area": area,
                "building": building,
                "district": "jvc"
            }
            
            # Build features
            X_input = build_features(user_input, model_columns)
            
            # Make prediction
            try:
                prediction = model.predict(X_input)[0]
                
                # Display results
                st.success("### Prediction Complete!")
                
                # Main prediction card
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    monthly = prediction / 12
                    st.metric(
                        "Monthly Rent",
                        f"{monthly:,.0f} AED",
                        delta=f"{(monthly - (avg_price/12)):+.0f}" if 'avg_price' in locals() else None
                    )
                
                with col_b:
                    st.metric(
                        "Annual Rent",
                        f"{prediction:,.0f} AED",
                        help="Predicted annual rental price"
                    )
                
                with col_c:
                    price_sqft = prediction / area
                    st.metric(
                        "Price per sqft",
                        f"{price_sqft:,.1f} AED",
                        delta=f"{(price_sqft - avg_ppsft):+.1f}" if 'avg_ppsft' in locals() else None
                    )
                
                # Market Comparison
                st.subheader("📊 Market Comparison")
                
                # Get comparable properties
                comparable = df[
                    (df['bedrooms_clean'] == bedrooms) &
                    (df['area_clean'].between(area * 0.8, area * 1.2))
                ]
                
                if len(comparable) > 0:
                    comp_avg = comparable['price_yearly_aed'].mean()
                    diff_pct = ((prediction - comp_avg) / comp_avg) * 100
                    
                    comparison_data = pd.DataFrame({
                        'Category': ['Your Property', 'Similar Properties', 'Market Average'],
                        'Price (AED)': [prediction, comp_avg, df['price_yearly_aed'].mean()]
                    })
                    
                    fig_comparison = px.bar(
                        comparison_data,
                        x='Category',
                        y='Price (AED)',
                        text_auto='.0f',
                        title=f"Your Property vs Market",
                        color='Category',
                        color_discrete_map={
                            'Your Property': '#FF6B6B',
                            'Similar Properties': '#4ECDC4',
                            'Market Average': '#45B7D1'
                        }
                    )
                    fig_comparison.update_traces(texttemplate='%{y:,} AED')
                    st.plotly_chart(fig_comparison, use_container_width=True)
                    
                    # Insight
                    if diff_pct > 5:
                        st.info(f"📈 Your property is estimated **{diff_pct:.1f}% higher** than similar listings.")
                    elif diff_pct < -5:
                        st.info(f"📉 Your property is estimated **{abs(diff_pct):.1f}% lower** than similar listings - good value!")
                    else:
                        st.info(f"⚖️ Your property is estimated within **{abs(diff_pct):.1f}%** of market rate.")
                

                # Add building premiums
                building_premiums = {
                    'Al Khail': 12000, 'Mirage': 15000, 'Park View': 8000,
                    'JVC Towers': 18000, 'Green Community': 20000,
                    'La Vie': 10000, 'Maple': 9000, 'Saba': 11000,
                    'Elan': 13000, 'Meydan': 16000, 'Platinum': 22000, 'Viva': 9500
                }

                
                # Features Breakdown
                with st.expander("🔍 View Feature Analysis"):
                    features_df = pd.DataFrame({
                        'Feature': ['Bedrooms', 'Bathrooms', 'Area', 'Building Premium'],
                        'Impact': [
                            f"+{bedrooms * 16500:,.0f} AED",
                            f"+{bathrooms * 7500:,.0f} AED",
                            f"+{area * 42:,.0f} AED",
                            f"+{building_premiums.get(building, 10000):,.0f} AED"
                        ]
                    })
                    st.dataframe(features_df, use_container_width=True)
                    
                    st.markdown(f"""
                    **Calculation Formula:**
                    ```
                    Base Price: 35,000 AED
                    + Bedrooms × 16,500 AED
                    + Bathrooms × 7,500 AED  
                    + Area × 42 AED/sqft
                    + Building Premium ({building}: {building_premiums.get(building, 10000):,} AED)
                    ± Market Variance
                    ```
                    """)
                
                # Download prediction
                prediction_data = pd.DataFrame({
                    'Property Details': ['Prediction', 'Bedrooms', 'Bathrooms', 'Area', 'Building'],
                    'Values': [f"{prediction:,.0f} AED", bedrooms, bathrooms, f"{area} sqft", building]
                })
                
                csv = prediction_data.to_csv(index=False)
                st.download_button(
                    label="📥 Download Prediction Report",
                    data=csv,
                    file_name="rent_prediction_report.csv",
                    mime="text/csv",
                    help="Download prediction details as CSV"
                )
                
            except Exception as e:
                st.error(f"Prediction error: {str(e)}")
                st.info("Using fallback calculation...")
                
                # Fallback calculation
                fallback_price = 35000 + (bedrooms * 16500) + (bathrooms * 7500) + (area * 42)
                fallback_price += building_premiums.get(building, 10000)
                
                st.metric("Estimated Annual Rent", f"{fallback_price:,.0f} AED")

# ============================================================================
# FOOTER & ADDITIONAL INFO
# ============================================================================
st.divider()

col_left, col_mid, col_right = st.columns(3)

with col_left:
    st.markdown("""
    **📊 Data Source**  
    Simulated JVC market data  
    Based on Dubai rental trends
    """)

with col_mid:
    st.markdown("""
    **🤖 ML Model**  
    Random Forest Regressor  
    Trained on realistic market data
    """)

with col_right:
    st.markdown("""
    **🔗 Live Demo**  
    Full project on [GitHub](https://github.com/AymanBerri/RealEstate_Analytics)  
    YouTube walkthrough available
    """)

st.markdown("""
<div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px; margin-top: 30px;'>
    <p style='color: #666; font-size: 0.9em;'>
        <b>Real Estate Analytics Dashboard</b> | Built with Streamlit & Plotly | 
        Deployed on Hugging Face Spaces<br>
        <i>For demonstration purposes. Data is simulated based on JVC market trends.</i>
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# CUSTOM CSS STYLING
# ============================================================================
st.markdown("""
<style>
    .stButton > button {
        background: linear-gradient(90deg, #FF6B6B 0%, #FF8E53 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 12px 28px;
        font-size: 16px;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: bold;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .metric-container {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)