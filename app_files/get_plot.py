import streamlit as st 
import duckdb
import plotly.express as px 
import pandas as pd

def get_plot():
    with duckdb.connect("data/data.duckdb") as con:
        route_data = con.sql(f"""
            SELECT lap,
                CASE WHEN {st.session_state['metric']} THEN altitude ELSE altitude*{3.2808399} END AS altitude, 
                distance/1000/{st.session_state['convert_scale']} AS distance, 
                gradient
            FROM CORE.dim_rides
            WHERE world='{st.session_state['world']}' AND route='{st.session_state['route']}'
        """).to_df()

    # Duplicate data for lapping
    #lap_data = route_data.loc[route_data["lap"]==1]
    #for lap in range(st.session_state["laps"]-1):
    #    lap_data.loc[:, "distance"] += (st.session_state["lap_length"]/st.session_state["convert_scale"])
    #    lap_data.loc[:, "lap"] += 1
    #    route_data = pd.concat([route_data, lap_data])


    fig = px.line(route_data, x="distance", y="altitude",
                    labels={"distance":f"Distance ({st.session_state['d_unit']})",
                            "altitude":f"Altitude ({st.session_state['a_unit']})"})
        
    route_data["dfmt"] = [f"{'{:.2f}'.format(round(d,2))} {st.session_state['d_unit']}" for d in route_data['distance']] 
    route_data["afmt"] = [f"{'{:.1f}'.format(round(a,2))} {st.session_state['a_unit']}" for a in route_data['altitude']] 
    route_data["gfmt"] = [f"{'{:.1f}'.format(round(g,2))}%" for g in route_data['gradient']] 


    fig.update_traces(mode="lines", customdata=route_data[["dfmt", "afmt", "gfmt"]],
                        hovertemplate="<b>Distance: %{customdata[0]}</b><br>" + 
                        "<b>Altitude: %{customdata[1]}</b><br>" +
                        "<b>Grade: %{customdata[2]}</b><br>" + 
                        "<extra></extra>"
                        )

    # - Add highlight 
    for _, highlight in st.session_state["notes_data_editor"][st.session_state["notes_data_editor"]["highlight"]].iterrows():
        if highlight["type"]=="lead":
            fig.add_vrect(x0=highlight["start_point"], x1=highlight["end_point"], fillcolor="pink", line_width=0, opacity=0.2)
        elif highlight["type"]=="sprint":
            fig.add_vrect(x0=highlight["start_point"], x1=highlight["end_point"], fillcolor="green", line_width=0, opacity=0.3)
        elif highlight["type"]=="climb":
            fig.add_vrect(x0=highlight["start_point"], x1=highlight["end_point"], fillcolor="red", line_width=0, opacity=0.3)
        else:
            fig.add_vrect(x0=highlight["start_point"], x1=highlight["end_point"], fillcolor="blue", line_width=0, opacity=0.3)

        if highlight["type"] in ["lead", "finish", "lap_banner"]:
            fig.add_vline(x=highlight["end_point"], line_color="blue")
    
    st.session_state["profile_plot"] = fig
