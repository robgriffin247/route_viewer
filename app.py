import streamlit as st 
from app_files.route_menu import route_menu
from app_files.lap_menu import lap_menu
from app_files.get_notes import get_notes
from app_files.get_plot import get_plot

st.set_page_config(
    page_title="RouteViewer",
    page_icon=":bike:"
)

st.title("RouteViewer")
st.write("Racing Notes for Zwift")
st.html("<hr/>")


route_menu()
profile_plot_cont = st.container()
lap_menu()
get_notes()
get_plot()
profile_plot_cont.plotly_chart(st.session_state["profile_plot"])


# ADD MORE DATA 






