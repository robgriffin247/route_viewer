import streamlit as st 
import duckdb
import pandas as pd
import os

def input_menu():
    with duckdb.connect(f"{os.getenv('DB')}") as con:
        routes = con.sql(f"SELECT * FROM {os.getenv('PRD_SCHEMA')}.dim_routes").to_df()


    world, route, metric = st.columns([4,6,3], vertical_alignment="bottom")

    world.selectbox("World", 
                    label_visibility="hidden",
                    index=routes.index[routes.world=="Watopia"].tolist()[0], # gets Watopia
                    options=routes.world,
                    key="world")

    route.selectbox("Route", 
                    label_visibility="hidden", 
                    options=routes.route[routes.world==st.session_state["world"]],
                    key="route")

    metric.toggle("Metric",
                value=True,
                key="metric")

