import duckdb
import streamlit as st
import inspect

data_config = st.secrets['data_config']

def dim_notes():
    print(f'Running {inspect.stack()[0][3]}...')

    with duckdb.connect(f'{data_config["data_directory"]}/{data_config["test_db"]}') as con:
        con.sql(f'create or replace table {data_config["schema_prd"]}.{inspect.stack()[0][3]} as select * from {data_config["schema_int"]}.int_{inspect.stack()[0][3].split("dim_")[1]}')
 