import streamlit as st 
import duckdb
import pandas as pd

def input_menu():
    with duckdb.connect("data/data.duckdb") as con:
        routes = con.sql(f"SELECT * FROM CORE.dim_routes").to_df()


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


    if st.session_state["metric"]:
        st.session_state["d_unit"] = "km"
        st.session_state["a_unit"] = "m"
        st.session_state["convert_scale"] = 1
    else:
        st.session_state["d_unit"] = "mi"
        st.session_state["a_unit"] = "ft"
        st.session_state["convert_scale"] = 1.609344

