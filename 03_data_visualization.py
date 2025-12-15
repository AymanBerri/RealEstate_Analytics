# Streamlit runs top to bottom and every time the user interacts (dropdown, slider), the script reruns
# st. functions = UI elements

# load data → show filters → draw charts → show insights


# Imports

import streamlit as st # The UI
import sqlite3          #Our DB
import pandas as pd     # Data handling. To create the data frame 
import plotly.express as px     #interactive charts


# ________________________________________________________________________
# Configure the Page
st.set_page_config(
    page_title="JVC Real Estate Analytics",
    layout="wide"
)


# ________________________________________________________________________
# Load DB (loading data from the DB)
@st.cache_data      # here Streamlit caches the data, to prevent 
                        #loading the DB every time the user interacts
def load_data():
    conn = sqlite3.connect("data/database.db")
    df = pd.read_sql("SELECT * FROM jvc_apartments", conn)
    conn.close()
    return df

df = load_data()

# ________________________________________________________________________
# Temporary feature engineering

# to get micro-market analysis
df["building"] = df["location"].str.split(",").str[0].str.strip()

# getting the price/sqft 
df["price_per_sqft"] = (
    df["price_yearly_aed"] / df["area_clean"]
)

# ________________________________________________________________________
# Setting the app header and context
st.title("JVC Apartment Rental Analytics")
st.markdown(
    """
    Interactive dashboard analyzing apartment rental listings in  
    **Jumeirah Village Circle (JVC), Dubai**, sourced from Bayut.
    """
)


# ________________________________________________________________________
# FILTERS
#   This is what allows the users to interact.
#   Filters is way for user to choose values that restrict the dataframe (DB)


filtered_df = df.copy()



# Bedrooms
bedroom_options = sorted(df["bedrooms_clean"].dropna().unique())
# UI element \/
selected_bedrooms = st.multiselect(
    "Bedrooms",
    options=bedroom_options,
    default=bedroom_options
)

# Gets only bedrooms selected and update the filtered_df
filtered_df = filtered_df[
    filtered_df["bedrooms_clean"].isin(selected_bedrooms)
]




# Yearly rent range
min_price, max_price = st.slider(
    "Yearly Rent Range (AED)",
    min_value=int(df["price_yearly_aed"].min()),
    max_value=int(df["price_yearly_aed"].max()),
    value=(
        int(df["price_yearly_aed"].min()),
        int(df["price_yearly_aed"].max())
    ),
    step=5000
)

filtered_df = filtered_df[
    (filtered_df["price_yearly_aed"] >= min_price) &
    (filtered_df["price_yearly_aed"] <= max_price)
]




# Area range filter - slider (size of the property)
min_area, max_area = st.slider(
    "Apartment Size (sqft)",
    min_value=int(df["area_clean"].min()),
    max_value=int(df["area_clean"].max()),
    value=(
        int(df["area_clean"].min()),
        int(df["area_clean"].max())
    ),
    step=50
)

filtered_df = filtered_df[
    (filtered_df["area_clean"] >= min_area) &
    (filtered_df["area_clean"] <= max_area)
]


# Building / Micro-location

# filter the building name. This provides micro-market analysis 
# Only top buildings (by num of listings)
top_buildings = (
    filtered_df["building"]
    .value_counts()
    .head(15)
    .index
    .tolist()
)

selected_buildings = st.multiselect(
    "Building (Top 15 by Listings)",
    options=top_buildings,
    default=top_buildings   #all buildings selected initially
)




# ALL BUILDINGS (noisy version)
# building_options = sorted(df["building"].unique())

# selected_buildings = st.multiselect(
#     "Building",
#     options=building_options,
#     default=[]
# )

if selected_buildings:
    filtered_df = filtered_df[
        filtered_df["building"].isin(selected_buildings)
    ]





# ________________________________________________________________________
# METRICS - KPIs. Showed at the top of the dashboard
col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Listings",
    len(filtered_df)
)

col2.metric(
    "Average Yearly Rent (AED)",
    f"{filtered_df['price_yearly_aed'].mean():,.0f}"
)

col3.metric(
    "Average Area (sqft)",
    f"{filtered_df['area_clean'].mean():,.0f}"
)



# CHARTS (Interactive charts using Plotly)


# Price distribution
fig_price = px.histogram(
    filtered_df,
    x="price_yearly_aed",
    nbins=30,
    title="Yearly Rental Price Distribution (AED)"
)

st.plotly_chart(fig_price, use_container_width=True)


# AVG price by bedroom
avg_price_bed = (
    filtered_df
    .groupby("bedrooms_clean")["price_yearly_aed"]
    .mean()
    .reset_index()
)

fig_bed = px.bar(
    avg_price_bed,
    x="bedrooms_clean",
    y="price_yearly_aed",
    title="Average Yearly Rent by Bedrooms",
    labels={
        "bedrooms_clean": "Bedrooms",
        "price_yearly_aed": "Avg Yearly Rent (AED)"
    }
)

st.plotly_chart(fig_bed, use_container_width=True)




# INSIGHTS
st.subheader("📌 Key Insights")

st.markdown("""

hellow world :D

""")









