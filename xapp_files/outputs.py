import streamlit as st 
import plotly.express as px

def notes_output():
    if st.session_state["note_data"].shape[0]==0:
        st.session_state["live_notes"] = None
        st.write("Sorry, there's no notes for that route yet! I'm working as fast as I can. I hope the route profile above is helpful in the meantime :)")
    else:
        st.session_state["live_notes"] = st.data_editor(st.session_state["note_data"][["type", "segment", "highlight", "start_point", "end_point", "note"]],
                        hide_index=True, 
                        height=int(35.2*(st.session_state["note_data"].shape[0]+1)),
                        use_container_width=True,
                        column_config={
                            "type":None,
                            "segment":st.column_config.TextColumn("Segment", width="medium"),
                            "highlight":st.column_config.CheckboxColumn("🚨"),
                            "start_point":st.column_config.NumberColumn("From", format=f"%.1f {st.session_state['units']['distance']}", width="small"),
                            "end_point":st.column_config.NumberColumn("To", format=f"%.1f {st.session_state['units']['distance']}", width="small"),
                            "note":st.column_config.TextColumn("Note", width="large")
                        }
                )


def profile_output():
    fig = px.line(st.session_state["ride_data"], 
                x="distance", 
                y="altitude",
                labels={"distance":f"Distance ({st.session_state['units']['distance']})",
                        "altitude":f"Altitude ({st.session_state['units']['altitude']})"})

    colours = {"sprint":"green", "climb":"red", "other":"blue"}
    if st.session_state["note_data"].shape[0]!=0:
        for _, note in st.session_state["live_notes"].iterrows():
            if note["highlight"]:
                fig.add_vrect(x0=note["start_point"], x1=note["end_point"], fillcolor=colours[note["type"]], line_width=0, opacity=0.2)

    fig.update_traces(mode="lines", customdata=st.session_state["ride_data"][["distance_tip", "altitude_tip", "gradient_tip"]],
                        hovertemplate="<b>Distance: %{customdata[0]}</b><br>" + 
                        "<b>Altitude: %{customdata[1]}</b><br>" +
                        "<b>Grade: %{customdata[2]}</b><br>" + 
                        "<extra></extra>"
                        )

    return fig
    