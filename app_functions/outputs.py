import streamlit as st 
import plotly.express as px

def notes_output():
    if st.session_state["note_data"].shape[0]==0:
        st.session_state["live_notes"] = None
        st.write("Sorry, there's no notes for that route yet! I'm working as fast as I can. I hope the route profile above is helpful in the meantime :)")
    else:
        st.session_state["live_notes"] = st.data_editor(st.session_state["note_data"][["type", "segment", "highlight", "start_point", "end_point", "note"]],
                        hide_index=True, 
                        #height=int(35.2*(st.session_state["note_data"].shape[0]+1)),
                        use_container_width=True,
                        column_config={
                            "type":None,
                            "segment":st.column_config.TextColumn("Segment", width="medium"),
                            "highlight":st.column_config.CheckboxColumn("🚨"),
                            "start_point":st.column_config.NumberColumn("From", format=f"%.2f {st.session_state['units']['distance']}", width="small"),
                            "end_point":st.column_config.NumberColumn("To", format=f"%.2f {st.session_state['units']['distance']}", width="small"),
                            "note":st.column_config.TextColumn("Note", width="large")
                        }
                )
    
    if not st.session_state["route_data"].loc[0, "circuit"]:
        st.write("Please note that the description for this route is currently incomplete - check back soon to see changes as I build my library of route data!")


def profile_output():
    data = st.session_state["ride_data"]
    fig = px.line(data, 
                x="distance", 
                y="altitude",
                #line_shape="spline",
                labels={"distance":f"Distance ({st.session_state['units']['distance']})",
                        "altitude":f"Altitude ({st.session_state['units']['altitude']})"})

    colours = {"sprint":"green", "climb":"red", "other":"blue"}
    if st.session_state["note_data"].shape[0]!=0:
        for _, note in st.session_state["live_notes"].iterrows():
            if note["highlight"]:
                fig.add_vrect(x0=note["start_point"], x1=note["end_point"], fillcolor=colours[note["type"]], line_width=0, opacity=0.2)

    fig.update_traces(mode="lines", customdata=data[["distance_tip", "altitude_tip", "gradient_tip"]],
                        hovertemplate="<b>Distance: %{customdata[0]}</b><br>" + 
                        "<b>Altitude: %{customdata[1]}</b><br>" +
                        "<b>Grade: %{customdata[2]}</b><br>" + 
                        "<extra></extra>"
                        )
    
    route_length = data["distance"].max()
    route_bottom = data["altitude"].min()
    route_top = data["altitude"].max()
    if route_top-route_bottom<50:  
        fig.update_yaxes(range=[route_bottom-10, route_top+60], minallowed=route_bottom-10, maxallowed=route_top+60)
        
    fig.update_xaxes(range=[0, route_length], minallowed=0, maxallowed=route_length)

    return fig