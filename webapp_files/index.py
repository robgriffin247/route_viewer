import streamlit as st
from webapp_functions.load_data import load_data
from webapp_functions.user_input_route import user_input_route
from webapp_functions.user_input_settings import user_input_settings
from webapp_functions.notes_table import notes_table
from webapp_functions.profile_plot import profile_plot

st.session_state["default_world"] = "Watopia"
st.session_state["default_route"] = "Oh Hill No"

load_data()
user_input_route()
user_input_settings()
profile_container = st.container()
notes_table()

profile_container.plotly_chart(profile_plot())
