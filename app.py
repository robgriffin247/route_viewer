import streamlit as st 
from webapp_functions.coffee import buy_coffee

page_config = st.secrets["page_config"]

st.set_page_config(
    page_title=page_config["page_name"],
    page_icon=page_config["page_icon"],
    initial_sidebar_state="collapsed",
)

# Styling
with open('./webapp_files/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Define navigation and pages
main_page = st.Page("webapp_files/index.py", 
                    title=f"{page_config['page_name']}")
about_page = st.Page("webapp_files/about.py", 
                     title=f"About {page_config['page_name']}")

pg = st.navigation([
    main_page, 
    about_page
    ])

# Set standard top of page
st.title(page_config["page_name"])
st.html("<h4>Racing Notes for Zwift</h4>")

pg.run()

buy_coffee()