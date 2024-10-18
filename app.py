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
main_page = st.Page("pages/index.py", title="Home")
about_page = st.Page("pages/about.py", title="About")
pg = st.navigation([main_page, about_page])

# Set standard top of page
st.title("RouteViewer")
st.html("""
        <div class='subheader''>Racing Notes for Zwift</div>
        """)

# Run the app
pg.run()


# TODO ===========================================
# Add to stg_rides to check if route already parsed (message duplicates; manual delete?)
# Build notes to cover lap banners (then reinstate can_lap flow control)