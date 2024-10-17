import streamlit as st 
from app_files.route_menu import route_menu
from app_files.controls import controls
from app_files.get_notes import get_notes
from app_files.get_plot import get_plot

route_menu()
controls()
profile_plot_cont = st.container()
get_notes()
get_plot()
profile_plot_cont.plotly_chart(st.session_state["profile_plot"])