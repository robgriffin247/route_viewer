import streamlit as st 


st.set_page_config(
    page_title="RouteViewer",
    page_icon=":bike:",
    #layout="wide",
    initial_sidebar_state="collapsed"
)

index_page = st.Page("main.py", title="Home")
about_page = st.Page("about.py", title="About")
pg = st.navigation([index_page, about_page])



st.title("RouteViewer")
st.write("Racing Notes for Zwift")
st.html("<hr/>")

pg.run()

