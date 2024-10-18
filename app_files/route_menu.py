import streamlit as st 
import duckdb
import pandas as pd
import numpy as np



def route_menu():
    with duckdb.connect("data/data.duckdb") as con:
        routes = con.sql(f"SELECT DISTINCT(world) AS world, route FROM CORE.dim_rides ORDER BY world, route").to_df()

    world, route = st.columns([4,6], vertical_alignment="bottom")

    st.write()
    world.selectbox("World", 
                    label_visibility="hidden",
                    index=int(np.where(routes.world.unique()=="Watopia")[0][0]),
                    options=routes.world.unique(),
                    key="world")

    if st.session_state["world"]=="Watopia":
        default_index=[i for i in routes.route[routes.world==st.session_state["world"]]].index("Glyph Heights")
    else:
        default_index=0

    route.selectbox("Route", 
                    #label_visibility="hidden", 
                    index=default_index,
                    options=routes.route[routes.world==st.session_state["world"]],
                    key="route")

    #st.session_state["can_lap"] = routes[(routes["world"]==st.session_state["world"]) & (routes["route"]==st.session_state["route"])]["can_lap"].values[0]
