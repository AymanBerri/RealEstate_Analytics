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
    conn = sqlite3.connect("../data/database.db")
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
st.title("JVC Apartment Rental Market Overview")

st.markdown(
    """
    A data-driven view of **apartment rental listings in Jumeirah Village Circle (JVC), Dubai**.  
    Built to explore pricing patterns, unit characteristics, and micro-market differences
    across buildings and unit types.
    """
)

# Create two columns to display the images side by side
col1, col2 = st.columns(2)

# First Image
col1.image("https://dubai-property.investments/uploads/images/2021-09/4-pano-evening-arw06136.jpg", caption="JVC Map", width=350)

# Second Image
col2.image("https://dubai-immo.com/wp-content/uploads/2023/02/map-localisation-jvc-dubai.png", caption="JVC Map", width=350)
# ________________________________________________________________________
# FILTERS
#   This is what allows the users to interact.
#   Filters is way for user to choose values that restrict the dataframe (DB)

st.sidebar.markdown("### Refine the Market View")
st.sidebar.caption("Use the filters below to explore specific unit types, price ranges, and buildings.")




# Bedrooms
bedroom_options = sorted(df["bedrooms_clean"].dropna().unique())
# UI element \/ - dropdown
selected_bedrooms = st.sidebar.multiselect(
    "Bedrooms",
    options=bedroom_options,
    default=bedroom_options
)

# Gets only bedrooms selected and update the filtered_df
filtered_df = filtered_df[
    filtered_df["bedrooms_clean"].isin(selected_bedrooms)
]


# Yearly rent range - slider
min_price, max_price = st.sidebar.slider(
    "Yearly Rent Range (AED)",
    min_value=int(df["price_yearly_aed"].min()),
    max_value=int(df["price_yearly_aed"].max()),
    value=(int(df["price_yearly_aed"].min()), int(df["price_yearly_aed"].max())),
    step=5000
)

filtered_df = filtered_df[
    (filtered_df["price_yearly_aed"] >= min_price) &
    (filtered_df["price_yearly_aed"] <= max_price)
]




# Area range filter - slider (size of the property)
min_area, max_area = st.sidebar.slider(
    "Apartment Size (sqft)",
    min_value=int(df["area_clean"].min()),
    max_value=int(df["area_clean"].max()),
    value=(int(df["area_clean"].min()), int(df["area_clean"].max())),
    step=50
)
filtered_df = filtered_df[
    (filtered_df["area_clean"] >= min_area) &
    (filtered_df["area_clean"] <= max_area)
]


# Building / Micro-location

# filter the building name. This provides micro-market analysis 
# Only top buildings (by num of listings)
top_buildings = filtered_df["building"].value_counts().head(15).index.tolist()
selected_buildings = st.sidebar.multiselect(
    "Building (Top 15 selected by default)",
    options=top_buildings,
    default=top_buildings,
)
if selected_buildings:
    filtered_df = filtered_df[filtered_df["building"].isin(selected_buildings)]


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
col1, col2, col3, col4 = st.columns(4)

col1.metric("Active Listings", len(filtered_df), delta_color="normal")
col2.metric("Avg. Annual Rent (AED)", f"{filtered_df['price_yearly_aed'].mean():,.0f}")
col3.metric("Avg. Unit Size (sqft)", f"{filtered_df['area_clean'].mean():,.0f}")
col4.metric("Avg. Price per sqft (AED)", f"{filtered_df['price_per_sqft'].mean():,.0f}")



# ________________________________________________________________________
# CHARTS (Interactive charts using Plotly)


# ###
# Price distribution
fig_price = px.histogram(
    filtered_df,
    x="price_yearly_aed",
    nbins=30,
    color="bedrooms_clean",            # color by bedroom type
    color_discrete_sequence=px.colors.qualitative.Set2,  
    title="Distribution of Annual Rents (AED)"
)

st.plotly_chart(fig_price, use_container_width=True)

# Price insights
if len(filtered_df) > 0:
    avg_price = filtered_df["price_yearly_aed"].mean()
    min_price_val = filtered_df["price_yearly_aed"].min()
    max_price_val = filtered_df["price_yearly_aed"].max()
    st.markdown(
        f"**Market Snapshot:** The average annual rent sits at **{avg_price:,.0f} AED**, "
        f"with listings spanning from **{min_price_val:,.0f} AED** up to **{max_price_val:,.0f} AED**."
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
    title="Average Annual Rent by Bedroom Count",
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
    st.markdown("**Pricing by Unit Type:** " + " · ".join(bed_lines))


if len(avg_price_bed) >= 2:
    min_bed = avg_price_bed.iloc[0]
    max_bed = avg_price_bed.iloc[-1]
    pct_diff = (
        (max_bed["price_yearly_aed"] - min_bed["price_yearly_aed"])
        / min_bed["price_yearly_aed"]
    ) * 100

    st.markdown(
        f"**Pricing Gradient:** Moving from **{int(min_bed['bedrooms_clean'])}-bedroom** units "
        f"to **{int(max_bed['bedrooms_clean'])}BR** increases average rent by "
        f"**{pct_diff:.1f}%**."
    )



# Rent vs Apartment Size
fig_scatter = px.scatter(
    filtered_df,
    x="area_clean",
    y="price_yearly_aed",
    color="bedrooms_clean",
    size="price_per_sqft",
    hover_data=["building", "location"],
    title="Rent vs Apartment Size",
    labels={"area_clean":"Size (sqft)", "price_yearly_aed":"Rent (AED)"}
)
st.plotly_chart(fig_scatter, use_container_width=True)

# Dynamic insight for scatter
if len(filtered_df) > 0:
    corr = filtered_df["area_clean"].corr(filtered_df["price_yearly_aed"])
    st.markdown(f"*Insight:* Rent and apartment size have a correlation of **{corr:.2f}** in the current filter set.")



# Listing Distribution by Bedroom
bedroom_counts = filtered_df["bedrooms_clean"].value_counts().reset_index()
bedroom_counts.columns = ["Bedrooms", "Count"]

fig_pie = px.pie(
    bedroom_counts,
    values="Count",
    names="Bedrooms",
    title="Listing Distribution by Bedroom Count",
    color_discrete_sequence=px.colors.qualitative.Set3
)
st.plotly_chart(fig_pie, use_container_width=True)


# Dynamic insight for pie chart
if len(filtered_df) > 0:
    top_bedroom = bedroom_counts.iloc[0]
    st.markdown(f"*Insight:* Most listings are **{top_bedroom['Bedrooms']}-BR units ({top_bedroom['Count']} listings)** under current filters.")



# ________________________________________________________________________
# Market Value Analysis

value_df = (
    filtered_df
    .groupby("building")["price_per_sqft"]
    .mean()
    .sort_values()
    .head(5)
)

st.subheader("Best Value Buildings")
st.caption("Ranked by lowest average rent per square foot among filtered listings.")
for bld, val in value_df.items():
    st.markdown(f"- **{bld}** — {val:,.0f} AED / sqft")





# ________________________________________________________________________
# INSIGHTS - AI Generated
st.subheader("Market Takeaways")

if len(filtered_df) > 0:
    # Top buildings by listing count
    top_buildings_text = ", ".join(
        [f"{b} ({c} listings)" for b, c in filtered_df["building"].value_counts().head(5).items()]
    )

    # Bedroom mix
    bedroom_mix = ", ".join(
        [f"{int(b)} BR ({c} listings)" for b, c in filtered_df["bedrooms_clean"].value_counts().items()]
    )

    st.markdown(f"""
- **Average Unit Size:** {filtered_df['area_clean'].mean():,.0f} sqft  
- **Average Annual Rent:** {filtered_df['price_yearly_aed'].mean():,.0f} AED  
- **Top Buildings by Listings:** {top_buildings_text}  
- **Bedroom Mix:** {bedroom_mix}  
- **Rent per sqft Range:** {filtered_df['price_per_sqft'].min():,.0f} AED — {filtered_df['price_per_sqft'].max():,.0f} AED  
- **Pricing Gradient:** 1-bedroom to largest units increases average rent by {pct_diff:.1f}%  
- **Best Value Building:** {value_df.idxmin()} — {value_df.min():,.0f} AED/sqft
""")
else:
    st.markdown("No listings available with the current filters.")



# st.subheader("Who This Dashboard Is For")
# st.markdown("""
# - **Tenants** — Understand fair rental ranges by unit size and building  
# - **Investors** — Identify value opportunities and pricing inefficiencies  
# - **Property managers** — Benchmark assets against nearby listings  
# - **Data teams** — Extend the pipeline to other Dubai communities
# """)

