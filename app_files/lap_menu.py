import streamlit as st 
import duckdb
import pandas as pd

def lap_menu():
    if st.session_state["can_lap"]:
        laps, custom_start, custom_finish = st.columns(3, vertical_alignment="bottom")
    
        laps.number_input("Laps", value=1, min_value=1, max_value=20, key="laps")
    
    else:
        st.session_state["laps"] = 1