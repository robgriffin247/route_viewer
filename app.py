# TODO
# - FEAT: note that notes are incomplete/lapping may not actually be possible

import duckdb
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
    about_page,
    ])

# Set standard top of page
st.title(page_config["page_name"])
st.html("<h4>Racing Notes for Zwift</h4>")

pg.run()


data_config = st.secrets["data_config"]





st.markdown('------')

with duckdb.connect(f'{data_config["data_directory"]}/{data_config["database_name"]}') as con:
    n_gpx = con.sql('select count(distinct(world, route)) as n from core.dim_rides').to_df()
    n_notes = con.sql('select count(distinct(world, route)) as n from core.dim_routes where complete_notes').to_df()
    st.write(str(int(n_gpx.loc[0, 'n'])) + ' route profiles loaded, ' + str(int(n_notes.loc[0, 'n'])) + ' fully annotated - I\'m working to get more routes finished as quickly as I can!')

st.write('This project has already and will continue to use a lot of my time. While I have chosen to make this free to use and open-source, you are welcome to show your appreciation and support by buying me coffee (or bike parts)!')

buy_coffee()