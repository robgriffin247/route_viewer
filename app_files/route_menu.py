import streamlit as st 
import duckdb
import pandas as pd
import numpy as np


def route_menu():
    with duckdb.connect("data/data.duckdb") as con:
        routes = con.sql(f"SELECT DISTINCT(world) AS world, route FROM CORE.dim_rides ORDER BY world, route").to_df()

    world, route = st.columns([4,6], vertical_alignment="bottom")

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
                    label_visibility="hidden", 
                    index=default_index,
                    options=routes.route[routes.world==st.session_state["world"]],
                    key="route")

    with duckdb.connect("data/data.duckdb") as con:
        st.session_state["route_data"] = con.sql(f"""
            SELECT lap, altitude, distance/1000 AS distance, gradient
            FROM CORE.dim_rides
            WHERE world='{st.session_state['world']}' AND route='{st.session_state['route']}'
        """).to_df()

        st.session_state["notes_data"] = con.sql(f"""
            SELECT 
                CASE WHEN ROW_NUMBER() OVER(ORDER BY start_point) = 1 OR LAG(segment) OVER()!=segment THEN segment ELSE '' END AS segment, 
                type, start_point, end_point, note,
                CASE WHEN type IN ('sprint', 'climb', 'finish', 'lap_banner') THEN true ELSE false END AS highlight
            FROM CORE.dim_notes
            WHERE world='{st.session_state['world']}' AND route='{st.session_state['route']}'
            ORDER BY start_point
            """).to_df()


    if len([i for i in st.session_state["notes_data"]["type"] if i=="lap_banner"]):
        st.session_state["can_lap"] = True
    else:
        st.session_state["can_lap"] = False
    