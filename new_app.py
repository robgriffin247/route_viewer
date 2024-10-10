import streamlit as st
import pandas as pd
import plotly.express as px 

from app_files.get_data import get_fit, get_notes
from app_files.visualise_data import create_profile_plot, create_notes_table

st.set_page_config(
    page_title="RouteViewer 2.0",
    page_icon=":bike:"
)

# USER INPUTS
world_input, route_input, metric_input = st.columns([4,6,2], vertical_alignment="bottom")
world_value = world_input.selectbox("World", options=get_fit().world.unique()) 
route_value = route_input.selectbox("Route", options=get_fit(world=world_value).route.unique()) 
metric_value = metric_input.toggle("Metric", value=True)

# FETCH DATA
focal_route_data = get_fit(world=world_value, route=route_value, metric=metric_value)
notes_data = get_notes(world=world_value, route=route_value, metric=metric_value)

# CREATE OUTPUTS
profile_plot = create_profile_plot(data=focal_route_data, metric=metric_value)
notes_table = create_notes_table(data=notes_data)

# TODO: Work on notes table


