
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

DATA_PATH = Path(
    r"C:\Users\count\Desktop\CAPSTONE\pls_fy2024_csv\CSV\pls_fy24_outlet_pud24i.csv"
)

@st.cache_data
def load_data():
    libraries = pd.read_csv(
        DATA_PATH,
        encoding="cp1252",
        low_memory=False
    )

    counties = [
        "ESCAMBIA",
        "SANTA ROSA",
        "OKALOOSA",
        "WALTON"
    ]

    regional = libraries[
        (libraries["STABR"] == "FL") &
        (libraries["CNTY"].isin(counties))
    ].copy()

    regional["LATITUDE"] = pd.to_numeric(
        regional["LATITUDE"], errors="coerce"
    )

    regional["LONGITUD"] = pd.to_numeric(
        regional["LONGITUD"], errors="coerce"
    )

    regional = regional.dropna(
        subset=["LATITUDE", "LONGITUD"]
    )

    regional = regional[
        regional["LATITUDE"].between(24, 32) &
        regional["LONGITUD"].between(-88, -80)
    ].copy()

    regional["LIBID"] = regional["LIBID"].astype(str)

    return regional.reset_index(drop=True)

libraries = load_data()

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
            search,
            case=False,
            na=False,
            regex=False
        )
    ]

selected_indices = []

if show_libraries:
    with st.sidebar.expander(
        "Individual Libraries",
        expanded=True
    ):
        for idx, row in filtered.iterrows():
            checked = st.checkbox(
                f"{row['LIBNAME']} ({row['CNTY']})",
                value=True,
                key=f"library_{idx}"
            )

            if checked:
                selected_indices.append(idx)

visible = filtered[
    filtered.index.isin(selected_indices)
].copy()

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
            float(row["LATITUDE"]),
            float(row["LONGITUD"])
        ],
        tooltip=str(row["LIBNAME"]),
        popup=folium.Popup(
            popup_html,
            max_width=300
        ),
        icon=folium.Icon(
            color="blue",
            icon="book"
        )
    ).add_to(m)

if len(visible) > 1:
    m.fit_bounds([
        [
            visible["LATITUDE"].min(),
            visible["LONGITUD"].min()
        ],
        [
            visible["LATITUDE"].max(),
            visible["LONGITUD"].max()
        ]
    ])

elif len(visible) == 1:
    m.location = [
        float(visible.iloc[0]["LATITUDE"]),
        float(visible.iloc[0]["LONGITUD"])
    ]
    m.zoom_start = 12

st_folium(
    m,
    height=650,
    width=None,
    returned_objects=[]
)

with st.expander("View Library Data"):
    st.dataframe(
        visible,
        use_container_width=True,
        hide_index=True
    )
