
import streamlit as st
import pandas as pd
import folium
import html
from pathlib import Path
from streamlit_folium import st_folium

st.set_page_config(
    page_title="AI Readiness Dashboard",
    layout="wide"
)

st.title("AI Readiness Dashboard")
st.caption("Northwest Florida — Public Library Accessibility")

# ---------------------------------
# LOAD DATA
# ---------------------------------

DATA_PATH = (
    Path(__file__).parent
    / "data"
    / "regional_libraries.csv"
)

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH, dtype={"LIBID": str})

libraries = load_data()

# ---------------------------------
# SIDEBAR CONTROLS
# ---------------------------------

st.sidebar.header("Geographic Filters")

counties = sorted(libraries["CNTY"].dropna().unique())

selected_counties = st.sidebar.multiselect(
    "Select Counties",
    options=counties,
    default=counties
)

filtered = libraries[
    libraries["CNTY"].isin(selected_counties)
].copy()

st.sidebar.divider()

st.sidebar.header("Resource Controls")

show_libraries = st.sidebar.checkbox(
    "Show Public Libraries",
    value=True
)

search = st.sidebar.text_input(
    "Search Libraries",
    placeholder="Enter library name..."
)

if search:
    filtered = filtered[
        filtered["LIBNAME"].str.contains(
            search, case=False, na=False, regex=False
        )
    ]

# ---------------------------------
# INDIVIDUAL LIBRARY SELECTION
# ---------------------------------

selected_ids = []

if show_libraries:
    with st.sidebar.expander(
        "Individual Libraries", expanded=True
    ):
        for _, row in filtered.iterrows():

            checked = st.checkbox(
                row["LIBNAME"],
                value=True,
                key=f"library_{row['LIBID']}"
            )

            if checked:
                selected_ids.append(row["LIBID"])

visible = filtered[
    filtered["LIBID"].isin(selected_ids)
].copy()

# ---------------------------------
# DASHBOARD METRICS
# ---------------------------------

col1, col2, col3 = st.columns(3)

col1.metric(
    "Libraries in Selected Counties",
    len(libraries[libraries["CNTY"].isin(selected_counties)])
)

col2.metric(
    "Libraries Displayed",
    len(visible)
)

col3.metric(
    "Counties Selected",
    len(selected_counties)
)

# ---------------------------------
# CREATE MAP
# ---------------------------------

m = folium.Map(
    location=[30.55, -86.85],
    zoom_start=9,
    tiles="OpenStreetMap"
)

for _, row in visible.iterrows():

    popup_html = f"""
    <b>{html.escape(str(row['LIBNAME']))}</b><br>
    County: {html.escape(str(row['CNTY']))}<br>
    City: {html.escape(str(row['CITY']))}<br>
    Address: {html.escape(str(row['ADDRESS']))}
    """

    folium.Marker(
        location=[
            row["LATITUDE"],
            row["LONGITUD"]
        ],
        tooltip=str(row["LIBNAME"]),
        popup=folium.Popup(popup_html, max_width=300),
        icon=folium.Icon(
            color="blue",
            icon="book"
        )
    ).add_to(m)

# Fit map to visible resources
if not visible.empty:
    bounds = [
        [
            visible["LATITUDE"].min(),
            visible["LONGITUD"].min()
        ],
        [
            visible["LATITUDE"].max(),
            visible["LONGITUD"].max()
        ]
    ]
    m.fit_bounds(bounds)

st_folium(
    m,
    height=650,
    width=None,
    returned_objects=[]
)

# ---------------------------------
# DATA TABLE
# ---------------------------------

with st.expander("View Library Data"):
    st.dataframe(
        visible,
        use_container_width=True,
        hide_index=True
    )





#--------------------------------
# Run Locally on Anaconda Prompt
#--------------------------------
#conda activate ai_readiness
#cd "%USERPROFILE%\Desktop\CAPSTONE\AI_Readiness_Dashboard"
#streamlit run app.py