import pandas as pd
import plotly.express as px
import streamlit as st

def create_profile_plot(data, metric):
    
    if metric:
        altitude_unit = "m"
        distance_unit = "km"
    else:
        altitude_unit = "ft"
        distance_unit = "miles"

    fig = px.line(data, x="distance", y="altitude",
                  labels={"distance":f"Distance ({distance_unit})",
                          "altitude":f"Altitude ({altitude_unit})"})

    fig.update_traces(mode="lines",
                      customdata=data[["formatted_distance", "formatted_altitude", "formatted_gradient"]],
                      hovertemplate=
                        "<b>Distance: %{customdata[0]}</b><br>" + 
                        "<b>Altitude: %{customdata[1]}</b><br>" + 
                        "<b>Grade: %{customdata[2]}</b><br>" + 
                        "<extra></extra>"
                     )
    
    st.plotly_chart(fig)


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


def create_notes_table(data):
    st.dataframe(data)