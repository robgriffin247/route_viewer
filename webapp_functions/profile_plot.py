import streamlit as st
import plotly.express as px 


def profile_plot():
    fig = px.area(data_frame=st.session_state["rides_focal"],
                  x="distance",
                  y="altitude",
                  hover_data=["gradient"],
                  labels={"distance":f"Distance ({st.session_state['dst_units']})",
                          "altitude":f"Altitude ({st.session_state['alt_units']})"})
    
    colours = {"sprint":"green", "climb":"red", None:"blue"}

    if st.session_state["notes_focal"].shape[0]!=0:
        for note in st.session_state["live_notes"].iter_rows():
            if note[0]:
                fig.add_vrect(x0=note[3], x1=note[4], fillcolor=colours[note[2]], line_width=0, opacity=0.2)
    
    if st.session_state["metric"]:
        fig.update_traces(mode="lines", customdata=st.session_state["rides_focal"][["gradient"]],
                        hovertemplate="<b>%{x:.2f} km</b><br>" + 
                        "<b>%{y:.0f} m</b><br>" + 
                        "<b>%{customdata[0]:.1f}%</b><br>" + 
                        "<extra></extra>"
                        )

    else:
        fig.update_traces(mode="lines", customdata=st.session_state["rides_focal"][["gradient"]],
                        hovertemplate="<b>%{x:.2f} mi</b><br>" + 
                        "<b>%{y:.0f} ft</b><br>" + 
                        "<b>%{customdata[0]:.1f}%</b><br>" + 
                        "<extra></extra>"
                        )

    return fig
