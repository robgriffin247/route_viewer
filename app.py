import streamlit as st 
import numpy as np

st.set_page_config(
    page_title="RouteViewer",
    page_icon=":bike:",
    initial_sidebar_state="collapsed"
)

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

index_page = st.Page("main.py", title="Home")
about_page = st.Page("about.py", title="About")
pg = st.navigation([index_page, about_page])

st.title("RouteViewer")
st.html("""
        <div class='subheader''>Racing Notes for Zwift</div>
        """)

pg.run()
