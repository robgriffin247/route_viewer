import duckdb
import streamlit as st

def load_data():
    for df in ["dim_routes", "dim_rides", "dim_notes"]:
        if df not in st.session_state:
            with duckdb.connect(f"{st.secrets['data_config']['data_directory']}/{st.secrets['data_config']['test_db']}", read_only=True) as con:
                st.session_state[df] = con.sql(f"select * from {st.secrets['data_config']['schema_prd']}.{df} order by world, route").pl()
