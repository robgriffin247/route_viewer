import streamlit as st 
import pandas as pd

def controls():
    laps, metric, _= st.columns([4,3,6], vertical_alignment="bottom")

    metric.toggle("Metric",
                value=True,
                key="metric")

    if st.session_state["metric"]:
        st.session_state["d_unit"] = "km"
        st.session_state["a_unit"] = "m"
    else:
        st.session_state["d_unit"] = "mi"
        st.session_state["a_unit"] = "ft"
        st.session_state["route_data"]["distance"] = st.session_state["route_data"]["distance"]/1.609344
        st.session_state["route_data"]["altitude"] = st.session_state["route_data"]["altitude"]*3.2808399
        st.session_state["notes_data"]["start_point"] = st.session_state["notes_data"]["start_point"]/1.609344
        st.session_state["notes_data"]["end_point"] = st.session_state["notes_data"]["end_point"]/1.609344

        
    #if st.session_state["can_lap"]:
    laps.number_input("Laps", value=1, min_value=1, max_value=20, key="laps")
    #else:
    #laps.number_input("Laps", value=1, min_value=1, max_value=1, key="laps", help="This route starts and finishes in different locations &mdash; it is not a loop &mdash; so laps do not work!")

    st.session_state["lap_route_data"] = st.session_state["route_data"].loc[st.session_state["route_data"]["lap"]==1]
    
    st.session_state["lap_length"] = st.session_state["lap_route_data"].iloc[-1]["distance"] - st.session_state["lap_route_data"].iloc[0]["distance"]
    
    st.session_state["lap_notes_data"] = st.session_state["notes_data"].loc[st.session_state["notes_data"]["start_point"]>=st.session_state["lap_route_data"].iloc[0]["distance"]]
    
    for lap in range(st.session_state["laps"]-1):
        st.session_state["lap_route_data"]["distance"] = st.session_state["lap_route_data"]["distance"] + st.session_state["lap_length"]
        st.session_state["route_data"] = pd.concat([st.session_state["route_data"], st.session_state["lap_route_data"]])
        
        st.session_state["lap_notes_data"]["start_point"] += st.session_state["lap_length"]
        st.session_state["lap_notes_data"]["end_point"] += st.session_state["lap_length"]
        st.session_state["notes_data"] = pd.concat([st.session_state["notes_data"], st.session_state["lap_notes_data"]])

