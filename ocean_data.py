import streamlit as st
import pydeck as pdk
import pandas as pd
import plotly.express as px
import time

st.set_page_config(page_title="Indian Ocean Floaters", layout="wide")
st.title("🌊 Indian Ocean Floater Tracking (Real Data)")

# ------------------------------------------------------------------
# Load dataset
# ------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("DATASET.csv")
    return df

df = load_data()

# Ensure sorting by time
df["time"] = pd.to_datetime(df["time"], errors="coerce")
df = df.sort_values(["float_id", "time"]).reset_index(drop=True)

# ------------------------------------------------------------------
# Organize floaters
# ------------------------------------------------------------------
floaters = {
    str(fid): grp[["latitude", "longitude"]].values.tolist()
    for fid, grp in df.groupby("float_id")
}

floater_data = {
    str(fid): grp.reset_index(drop=True)
    for fid, grp in df.groupby("float_id")
}

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
    if step < len(path):
        lat, lon = path[step]
        return pd.DataFrame([{"lat": lat, "lon": lon}])
    return pd.DataFrame([])

def get_trails(path, step):
    if step < len(path):
        return pd.DataFrame([{"path": [[lon, lat] for lat, lon in path[:step+1]]}])
    return pd.DataFrame([])

# ------------------------------------------------------------------
# Map initial state
# ------------------------------------------------------------------
view_state = pdk.ViewState(latitude=0, longitude=70, zoom=2)
deck_chart = st.empty()
info_box = st.empty()  # for showing floater info

# ------------------------------------------------------------------
# Animate only selected floater
# ------------------------------------------------------------------
path = floaters[selected_floater]
data = floater_data[selected_floater]

if animate:
    steps = len(path)
    for step in range(steps):
        df_frame = get_frame(path, step)
        trails_df = get_trails(path, step)

        scatter_layer = pdk.Layer(
            "ScatterplotLayer",
            df_frame,
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
            map_style=None,
            tooltip={"text": f"{selected_floater}: Step {step}"}
        )

        deck_chart.pydeck_chart(r)

        # Show current info (temperature, salinity, pressure)
        current_row = data.iloc[step]
        info_box.info(
            f"**Floater {selected_floater} | Step {step+1}/{steps}**\n\n"
            f"📍 Location: ({current_row['latitude']:.2f}, {current_row['longitude']:.2f})\n"
            f"🌡️ Temperature: {current_row['temperature']:.2f} °C\n"
            f"🧂 Salinity: {current_row['salinity']:.2f} PSU\n"
            f"⏱️ Pressure: {current_row['pressure']:.2f} dbar\n"
            f"🕒 Time: {current_row['time']}"
        )

        time.sleep(0.5)  # animation speed

    # Show graph after animation ends
    st.subheader(f"📊 Ocean Data for Floater {selected_floater}")
    fig = px.line(
        data,
        x="time",
        y=["temperature", "salinity", "pressure"],
        title=f"Ocean Parameters along Floater {selected_floater}'s Path",
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    # Static map (show all floaters initial positions)
    all_points = []
    for name, path in floaters.items():
        if path:  # not empty
            lat, lon = path[0]
            all_points.append({"lat": lat, "lon": lon, "floater": name})

    df_points = pd.DataFrame(all_points)

    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        df_points,
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
