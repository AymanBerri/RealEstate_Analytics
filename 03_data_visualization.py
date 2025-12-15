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


    # Temporary feature engineering

        # to get micro-market analysis
    df["building"] = df["location"].str.split(",").str[0].str.strip()

        # getting the price/sqft 
    df["price_per_sqft"] = df["price_yearly_aed"] / df["area_clean"]

    return df

df = load_data()

filtered_df = df.copy() # create copy


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

# Bedrooms
bedroom_options = sorted(df["bedrooms_clean"].dropna().unique())
# UI element \/ - dropdown
selected_bedrooms = st.multiselect(
    "Bedrooms",
    options=bedroom_options,
    default=bedroom_options
)

# Gets only bedrooms selected and update the filtered_df
filtered_df = filtered_df[
    filtered_df["bedrooms_clean"].isin(selected_bedrooms)
]


# Yearly rent range - slider
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


# ALL BUILDINGS (noisy version) (uncomment and comment the one above for full filtering flexibility)
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

col1.metric("Total Listings", len(filtered_df))
col2.metric("Average Yearly Rent (AED)", f"{filtered_df['price_yearly_aed'].mean():,.0f}")
col3.metric("Average Area (sqft)", f"{filtered_df['area_clean'].mean():,.0f}")


# ________________________________________________________________________
# CHARTS (Interactive charts using Plotly)


# ###
# Price distribution
fig_price = px.histogram(
    filtered_df,
    x="price_yearly_aed",
    nbins=30,
    title="Yearly Rental Price Distribution (AED)"
)

st.plotly_chart(fig_price, use_container_width=True)

# Price insights
if len(filtered_df) > 0:
    avg_price = filtered_df["price_yearly_aed"].mean()
    min_price_val = filtered_df["price_yearly_aed"].min()
    max_price_val = filtered_df["price_yearly_aed"].max()
    st.markdown(
        f"**Price Insight:** Listings show an average rent of **{avg_price:,.0f} AED**, "
        f"ranging from **{min_price_val:,.0f} AED** to **{max_price_val:,.0f} AED**."
    )




# ###
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

# Bedroom insights
if not avg_price_bed.empty:
    bed_lines = [
        f"{int(row['bedrooms_clean'])} BR ~ {int(row['price_yearly_aed']):,} AED"
        for _, row in avg_price_bed.iterrows()
    ]
    st.markdown(
        "**Bedroom Insight:** " +
        "; ".join(bed_lines)
    )

if len(avg_price_bed) >= 2:
    min_bed = avg_price_bed.iloc[0]
    max_bed = avg_price_bed.iloc[-1]
    pct_diff = (
        (max_bed["price_yearly_aed"] - min_bed["price_yearly_aed"])
        / min_bed["price_yearly_aed"]
    ) * 100

    st.markdown(
        f"**Market Signal:** Moving from **{int(min_bed['bedrooms_clean'])}BR** "
        f"to **{int(max_bed['bedrooms_clean'])}BR** increases average rent by "
        f"**{pct_diff:.1f}%**."
    )


# ________________________________________________________________________
# Market Value Analysis

value_df = (
    filtered_df
    .groupby("building")["price_per_sqft"]
    .mean()
    .sort_values()
    .head(5)
)

st.subheader("Best Value Buildings (Lowest Price per Sqft)")
for bld, val in value_df.items():
    st.markdown(f"- **{bld}**: {val:,.0f} AED/sqft")


# ________________________________________________________________________
# INSIGHTS - AI Generated
st.subheader("Key Insights")


if len(filtered_df) > 0:
    bld_counts = filtered_df["building"].value_counts().head(5)
    bld_text = ", ".join([f"{b} ({c} listings)" for b, c in bld_counts.items()])
    st.markdown(
        f"- The average area of filtered listings is **{filtered_df['area_clean'].mean():,.0f} sqft**.\n"
        f"- Top buildings by listing count: **{bld_text}**.\n"
        f"- The price per sqft ranges from **{filtered_df['price_per_sqft'].min():,.0f} AED** "
        f"to **{filtered_df['price_per_sqft'].max():,.0f} AED** with an average of **{filtered_df['price_per_sqft'].mean():,.0f} AED**."
    )
else:
    st.markdown("No listings available with the current filters.")


st.subheader("\nWho Is This Dashboard Useful For?")

st.markdown("""
- **Tenants** → Identify fair rental ranges by unit size  
- **Investors** → Compare yield potential by building  
- **Property managers** → Monitor market positioning  
- **Data teams** → Reuse pipeline for other Dubai communities
""")
