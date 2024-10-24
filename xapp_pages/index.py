import streamlit as st 
from xapp_files.user_inputs import route_input, controls_input
from xapp_files.outputs import notes_output, profile_output

from dotenv import load_dotenv
load_dotenv()


route_input()
controls_input()
plot_container = st.container()
notes_output()
plot_container.plotly_chart(profile_output())
