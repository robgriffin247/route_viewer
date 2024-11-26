import streamlit as st
from webapp_functions.load_data import load_data
from webapp_functions.user_input_route import user_input_route
from webapp_functions.user_input_settings import user_input_settings
from webapp_functions.notes_table import notes_table
from webapp_functions.profile_plot import profile_plot

st.session_state["default_world"] = "New York"
st.session_state["default_route"] = "Mighty Metropolitan"

load_data()
user_input_route()
user_input_settings()

# Container used because plot needs to update in response to live notes table (below it) 
profile_container = st.container()

with st.expander("Map"):
    st.map(data=st.session_state["rides_focal"], latitude="latitude", longitude  ="longitude", size=1, height=650)

with st.expander("Notes", expanded=(st.session_state["notes_focal"].height>0)):
    notes_table()

profile_container.plotly_chart(profile_plot())
