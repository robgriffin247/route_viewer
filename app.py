import streamlit as st
import duckdb
import plotly.graph_objects as go

col1, col2, col3 = st.columns(3)

with duckdb.connect("data/data.duckdb") as con:
    # User input to select world
    worlds = con.sql(f"""SELECT WORLD FROM INTERMEDIATE.OBT_FIT""").to_df()
    world = col1.selectbox("World", worlds.world.unique(), index=len(list(worlds.world.unique()))-1)

    # User input to select route (as a child of world)
    routes = con.sql(f"""SELECT ROUTE FROM INTERMEDIATE.OBT_FIT WHERE WORLD='{world}'""").to_df()
    route = col2.selectbox("Route", routes.route.unique())

    # User input to set the number of laps to generate
    col3.number_input("Laps", min_value=1, max_value=1, value=1, step=1)

    # Get the route data
    fit_data = con.sql(f"""SELECT * 
                       FROM INTERMEDIATE.OBT_FIT 
                       WHERE WORLD='{world}' AND ROUTE='{route}'""").to_df()

# Frontend:        
route_profile = go.Figure()

route_profile.add_trace(go.Scatter(
    x=fit_data["distance"], 
    y=fit_data["altitude"], 
    mode="lines"))

route_profile.update_layout(
    xaxis_title="Distance (km)", 
    yaxis_title="Altitude (m)")

st.plotly_chart(route_profile)
