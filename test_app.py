import streamlit as st 
from app_files.input_menu import input_menu
#from app_files.get_notes import get_notes


import duckdb
import os

st.set_page_config(
    page_title="RouteViewer",
    page_icon=":bike:"
)

st.title("RouteViewer")
st.write("Racing Notes for Zwift")
st.html("<hr/>")

input_menu()
world = st.session_state["world"] 
route = st.session_state["route"] 
metric = st.session_state["metric"] 



# Develop the function here then move to get_notes() - to reduce save and refresh process
def get_notes(world, route):
    with duckdb.connect(os.getenv('DB')) as con:
        return con.sql(f"""SELECT * 
                            FROM {os.getenv('PRD_SCHEMA')}.dim_notes 
                            WHERE world='{world}' AND route='{route}'""").to_df()
    
st.write(get_notes(world, route))
 
