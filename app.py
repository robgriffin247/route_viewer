import streamlit as st 
import numpy as np

st.set_page_config(
    page_title="RouteViewer",
    page_icon=":bike:",
    initial_sidebar_state="collapsed"
)

# Styling
st.html("""
        <style>
            .st-emotion-cache-13ln4jf { // Main page width
                max-width: 1000px; 
                width: 92%;
            }
        
            .subheader {
                color: #478f84;
                padding-bottom: 1em;
                margin-bottom: 1.6em;
                border-bottom: 1px dashed #525756;
            }
            
            a, a:visited {
                color: #478f84;
                transition: 0.2s;
            }
        
            a:hover, a:active {
                color: orange;
            }
        </style>
        """)


# Define navigation and pages
main_page = st.Page("app_pages/index.py", title="Home")
data_page = st.Page("app_pages/data.py", title="Wanted gpx files")
about_page = st.Page("app_pages/about.py", title="About")
pg = st.navigation([main_page, data_page, about_page])

# Set standard top of page
st.title("RouteViewer")
st.html("""
        <div class='subheader'>Racing Notes for Zwift</div>
        """)


pg.run()


