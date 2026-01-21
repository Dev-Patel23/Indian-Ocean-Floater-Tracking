 Indian Ocean Floater Tracking System 

An interactive data visualization application built with Streamlit to track and analyze the movement of ocean floaters in the Indian Ocean using real observational data.

  Project Overview
This project visualizes the trajectories of multiple ocean floaters over time and provides insights into key oceanographic parameters such as temperature, salinity, and pressure. Users can select individual floaters and watch their movement animated on a map, followed by analytical plots.

  Features
- Interactive map-based visualization
- Animated floater trajectories over time
- Multiple floater selection via sidebar controls

  Tech Stack
- Frontend & App Framework: Streamlit  
- Data Processing: Pandas  
- Geospatial Visualization: PyDeck  
- Graphing & Analysis: Plotly  
- Language:Python  

  Dataset
The dataset contains time-series data for multiple ocean floaters, including:
- `float_id`
- `latitude`
- `longitude`
- `temperature`
- `salinity`
- `pressure`
- `time`

  How to Run the Project
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/indian-ocean-floater-tracking.git


Install Dependencies
pip install streamlit pandas pydeck plotly

Run the Application
streamlit run app.py


