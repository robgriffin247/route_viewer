import streamlit as st 
from webapp_functions.user_inputs import route_input, controls_input
from webapp_functions.outputs import notes_output, profile_output

route_input()
controls_input()
plot_container = st.container()
notes_output()
plot_container.plotly_chart(profile_output())