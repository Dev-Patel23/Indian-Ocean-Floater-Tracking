import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import plotly.express as px
import time

st.set_page_config(page_title="Indian Ocean Floaters", layout="wide")
st.title("🌊 Indian Ocean Floater Tracking (Dummy Data)")

# ------------------------------------------------------------------
# Create 10 dummy floater paths (slightly different locations)
# ------------------------------------------------------------------
floaters = {
    f"Floater {i+1}": [
        [np.random.uniform(-20, 20) + step * 0.5,  # lat
         np.random.uniform(50, 80) + step * 0.5]   # lon
        for step in range(6)
    ]
    for i in range(10)
}

# ------------------------------------------------------------------
# Generate dummy ocean data for each floater
# ------------------------------------------------------------------
def generate_ocean_data(path):
    steps = len(path)
    return pd.DataFrame({
        "step": range(steps),
        "temperature": np.linspace(28, 22, steps) + np.random.normal(0, 0.3, steps),
        "salinity": np.linspace(34.5, 35.5, steps) + np.random.normal(0, 0.05, steps),
        "pH": np.linspace(8.15, 8.05, steps) + np.random.normal(0, 0.01, steps),
    })

floater_data = {name: generate_ocean_data(path) for name, path in floaters.items()}

# ------------------------------------------------------------------
# Sidebar controls
# ------------------------------------------------------------------
st.sidebar.header("Controls")
selected_floater = st.sidebar.radio("Select a Floater", list(floaters.keys()))
animate = st.sidebar.button("Animate Selected Floater")

# ------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------
def get_frame(path, step):
    """Return one position at a time"""
    if step < len(path):
        lat, lon = path[step]
        return pd.DataFrame([{"lat": lat, "lon": lon}])
    return pd.DataFrame([])

def get_trails(path, step):
    """Return trail (path covered so far)"""
    if step < len(path):
        return pd.DataFrame([{"path": [[lon, lat] for lat, lon in path[:step+1]]}])
    return pd.DataFrame([])

# ------------------------------------------------------------------
# Map initial state
# ------------------------------------------------------------------
view_state = pdk.ViewState(latitude=0, longitude=70, zoom=2)
deck_chart = st.empty()  # placeholder for map

# ------------------------------------------------------------------
# Animate only selected floater
# ------------------------------------------------------------------
path = floaters[selected_floater]
data = floater_data[selected_floater]

if animate:
    steps = len(path)
    for step in range(steps):
        df = get_frame(path, step)
        trails_df = get_trails(path, step)

        scatter_layer = pdk.Layer(
            "ScatterplotLayer",
            df,
            get_position='[lon, lat]',
            get_fill_color='[255, 0, 0]',
            get_radius=30000,
            pickable=True,
        )

        path_layer = pdk.Layer(
            "PathLayer",
            trails_df,
            get_path="path",
            get_color=[0, 0, 255],
            width_scale=2,
            width_min_pixels=2,
        )

        r = pdk.Deck(
            layers=[path_layer, scatter_layer],
            initial_view_state=view_state,
            map_style=None,   # OpenStreetMap
            tooltip={"text": f"{selected_floater}: Step {step}"}
        )

        deck_chart.pydeck_chart(r)
        time.sleep(1)

    # Show graph after animation
    st.subheader(f"📊 Ocean Data for {selected_floater}")
    fig = px.line(
        data,
        x="step",
        y=["temperature", "salinity", "pH"],
        title=f"Ocean Parameters along {selected_floater}'s Path",
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    # Static map (show all floaters initial positions)
    all_points = []
    for name, path in floaters.items():
        lat, lon = path[0]
        all_points.append({"lat": lat, "lon": lon, "floater": name})

    df = pd.DataFrame(all_points)

    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        df,
        get_position='[lon, lat]',
        get_fill_color='[0, 200, 0]',
        get_radius=25000,
        pickable=True,
    )

    r = pdk.Deck(
        layers=[scatter_layer],
        initial_view_state=view_state,
        map_style=None,
        tooltip={"text": "{floater}"}
    )

    deck_chart.pydeck_chart(r)
    st.info("👆 Select a floater from the sidebar and click 'Animate Selected Floater' to see its journey.")
