import streamlit as st 
import duckdb
import pandas as pd

def route_menu():
    with duckdb.connect("data/data.duckdb") as con:
        routes = con.sql(f"SELECT * FROM CORE.dim_routes ORDER BY world, route").to_df()
   
    #world, route, metric = st.columns([4,6,3], vertical_alignment="bottom")
    world, route, laps = st.columns([4,6,3], vertical_alignment="bottom")

    world.selectbox("World", 
                    #label_visibility="hidden",
                    index=routes.index[routes.world=="Watopia"].tolist()[0], # gets Watopia
                    options=routes.world.unique(),
                    key="world")

    route.selectbox("Route", 
                    #label_visibility="hidden", 
                    options=routes.route[routes.world==st.session_state["world"]],
                    key="route")

    st.session_state["can_lap"] = routes[(routes["world"]==st.session_state["world"]) & (routes["route"]==st.session_state["route"])]["can_lap"].values[0]

    if st.session_state["can_lap"]:
        laps.number_input("Laps", value=1, min_value=1, max_value=20, key="laps")
    
    else:
        laps.number_input("Laps", value=1, min_value=1, max_value=1, key="laps", help="This route starts and finishes in different locations &mdash; it is not a loop &mdash; so laps do not work!")


