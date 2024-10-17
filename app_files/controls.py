import streamlit as st 
import duckdb
import pandas as pd
import webbrowser

def controls():
    metric, basic, _= st.columns([2,3,6], vertical_alignment="bottom")
  
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

    
    basic.toggle("Full notes",
                value=True,
                help="Show comprehensive notes detailing the entire route or just the segments",
                key="basic")
