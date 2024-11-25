import streamlit as st
import polars as pl

def user_input_route():
  
    world_input, route_input = st.columns([4,6])

    world_index = int(st.session_state["dim_routes"].unique(subset=["world"], maintain_order=True).with_row_index().filter(pl.col("world")==st.session_state["default_world"])["index"].item())
    
    world_input.selectbox("World", key="world", index=world_index, 
                          options=st.session_state["dim_routes"].unique(subset=["world"], maintain_order=True).select("world"))
    
    # TODO add default world to session state (not changed anywhere) then get route index to a default route
    if st.session_state["world"] == st.session_state["default_world"]:
        route_index = int(st.session_state["dim_routes"].filter(pl.col("world")==st.session_state["world"]).with_row_index().filter(pl.col("world")==st.session_state["world"]).filter(pl.col("route")==st.session_state["default_route"])["index"].item())
    else:
        route_index = 0

    route_input.selectbox("Route", key="route", index=route_index, 
                          options=st.session_state["dim_routes"].filter(pl.col("world")==st.session_state["world"]).unique(subset=["route"], maintain_order=True).select("route"))

    st.session_state["routes_focal"] = st.session_state["dim_routes"].filter((pl.col("world")==st.session_state["world"]) & (pl.col("route")==st.session_state["route"]))
    st.session_state["rides_focal"] = st.session_state["dim_rides"].filter((pl.col("world")==st.session_state["world"]) & (pl.col("route")==st.session_state["route"])).sort(["distance"])
    st.session_state["notes_focal"] = st.session_state["dim_notes"].filter((pl.col("world")==st.session_state["world"]) & (pl.col("route")==st.session_state["route"])).sort(["note_start", "note_end", "note_type"])
