import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

def create_output(data, notes, metric):
    
    plot_container = st.container()

    if metric:
        altitude_unit = "m"
        distance_unit = "km"
    else:
        altitude_unit = "ft"
        distance_unit = "miles"


    fig = px.line(data, x="distance", y="altitude",
                  labels={"distance":f"Distance ({distance_unit})",
                          "altitude":f"Altitude ({altitude_unit})"})
    

    for i in notes.iterrows():
        if i[1]["type"]=="lead":
            color = "orange"
        elif i[1]["type"]=="sprint":
            color = "green"
        elif i[1]["type"]=="climb":
            color = "red"
        else:
            color = None

        fig.add_vrect(x0 = i[1]["from"], x1 = i[1]["to"], fillcolor=color, line_width=0, opacity=0.3)


    fig.update_traces(mode="lines",
                      customdata=data[["formatted_distance", "formatted_altitude", "formatted_gradient"]],
                      hovertemplate=
                        "<b>Distance: %{customdata[0]}</b><br>" + 
                        "<b>Altitude: %{customdata[1]}</b><br>" + 
                        "<b>Grade: %{customdata[2]}</b><br>" + 
                        "<extra></extra>"
                     )

    base_table = st.dataframe(notes[["segment", "from", "to", "notes"]],
                              use_container_width=True,
                              hide_index=True,
                              on_select="rerun",
                              selection_mode="multi-row",
                              column_config={
                                  "segment":st.column_config.TextColumn("Segment", width="medium"),
                                  "from":st.column_config.NumberColumn("From", width="small"),
                                  "to":st.column_config.NumberColumn("To", width="small"),
                                  "notes":st.column_config.TextColumn("Notes", width="large")
                              },
                              key="notes_table")      
    base_table

    plot_container.plotly_chart(fig)


def create_summary_table(data, metric):
    
    if metric:
        altitude_unit = "m"
    else:
        altitude_unit = "ft"

    distance = data.iloc[-1]["formatted_distance"]
    total_climbing = f"{data.loc[data['delta_altitude']>0, 'delta_altitude'].sum().round(2)} {altitude_unit}"

    output = f"""
        - Distance: {distance}
        - Total Climbing: {total_climbing}
        """
    
    st.markdown(output)
