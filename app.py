# TODO; add limits to axis ranges
import streamlit as st
from webapp_functions.coffee import buy_coffee
import sys


data_config = st.secrets["data_config"]
page_config = st.secrets["page_config"]


# Set default route
st.session_state["default_world"] = "Watopia"
st.session_state["default_route"] = "Tair Dringfa Fechan"


st.set_page_config(
    page_title=page_config["page_name"],
    page_icon=page_config["page_icon"],
    initial_sidebar_state="collapsed",
    layout="wide",
)




# Styling
with open("./webapp_files/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Set standard top of page
st.title(page_config["page_name"])
st.html("<h4>Racing Notes for Zwift</h4>")

# Define navigation and pages
main_page = st.Page("webapp_files/index.py", title=f"{page_config['page_name']}")
about_page = st.Page("webapp_files/about.py", title=f"About {page_config['page_name']}")

pg = st.navigation(
    [
        main_page,
        about_page,
    ]
)


# Run the selected page
pg.run()


# Link for buymeacoffee
buy_coffee()
