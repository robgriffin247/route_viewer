import streamlit as st 
import duckdb
import pandas as pd

def lap_menu():
    laps, custom_start, custom_finish = st.columns(3, vertical_alignment="bottom")
    
    laps.number_input("Laps", value=1, min_value=1, max_value=20, key="laps")
    custom_finish.number_input("Custom Finish", min_value=0, max_value=1000, key="custom_finish")
    custom_start.number_input("Custom Start", value=None, min_value=0, max_value=st.session_state["custom_finish"], key="custom_start")