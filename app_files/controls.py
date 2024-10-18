import streamlit as st 
import duckdb
import pandas as pd
import webbrowser

def controls():
    #laps, metric, _= st.columns([4,3,6], vertical_alignment="bottom")
    metric, _ = st.columns([2,9], vertical_alignment="bottom")
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

    
    #if st.session_state["can_lap"]:
    #laps.number_input("Laps", value=1, min_value=1, max_value=20, key="laps")
    
    #else:
    #    laps.number_input("Laps", value=1, min_value=1, max_value=1, key="laps", help="This route starts and finishes in different locations &mdash; it is not a loop &mdash; so laps do not work!")


