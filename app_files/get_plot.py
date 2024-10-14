import streamlit as st 
import duckdb
import plotly.express as px 
import pandas as pd

def get_plot():
    with duckdb.connect("data/data.duckdb") as con:
        df = con.sql(f"""
                     SELECT 
                        CASE WHEN {st.session_state['metric']} THEN distance_met ELSE distance_imp END AS distance,
                        CASE WHEN {st.session_state['metric']} THEN distance_met_fmt ELSE distance_imp_fmt END AS distance_fmt,
                        CASE WHEN {st.session_state['metric']} THEN altitude_met ELSE altitude_imp END AS altitude,
                        CASE WHEN {st.session_state['metric']} THEN altitude_met_fmt ELSE altitude_imp_fmt END AS altitude_fmt,
                        gradient_fmt
                     FROM CORE.dim_fits 
                     WHERE world='{st.session_state['world']}' 
                        AND route='{st.session_state['route']}'
                    """).to_df()

    #lead = df[df["distance"]<=st.session_state["lead_length"]]
    lap_df = df[df["distance"]>st.session_state["lead_length"]]

    for lap in range(st.session_state["laps"]-1):
        lap_df["distance"] += st.session_state["lap_length"]
        df = pd.concat([df, lap_df])

    st.session_state["profile_plot"] = px.line(df, x="distance", y="altitude", 
                                               range_x=[0, min([60,max(df["distance"])])],
                                               labels={
                                                    "distance":f"Distance ({st.session_state['d_unit']})",
                                                    "altitude":f"Altitude ({st.session_state['a_unit']})"
                                                    })
    
    for row, _ in enumerate(st.session_state["notes"].values):
        if st.session_state["notes_data_editor"].iloc[row].highlight:
            if st.session_state["notes"].iloc[row].type == "sprint":
                color = "green"
            elif st.session_state["notes"].iloc[row].type == "climb":
                color = "red"
            elif st.session_state["notes"].iloc[row].type == "lead":
                color = "pink"
            elif st.session_state["notes"].iloc[row].type == "finish":
                st.session_state["profile_plot"].add_vline(x=st.session_state["notes"].iloc[row].end_point,line_color="orange")
            else:
                color = "blue"
            
            st.session_state["profile_plot"].add_vrect(x0=st.session_state["notes"].iloc[row].start_point, 
                                                        x1=st.session_state["notes"].iloc[row].end_point, 
                                                        line_width=0, fillcolor=color, opacity=0.3)


    #st.session_state["profile_plot"].update_traces(mode="lines",
                        #customdata=df[["distance_fmt", "altitude_fmt", "gradient_fmt"]],
                        #hovertemplate="<b>Distance: %{customdata[0]}</b><br>" + "<b>Altitude: %{customdata[1]}</b><br>" +
                         #"<b>Grade: %{customdata[2]}</b><br>" + 
                        # "<extra></extra>"
     #                   )
