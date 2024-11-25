import duckdb
import streamlit as st
import pandas as pd
import inspect

# Setup database names and locations
data_config = st.secrets['data_config']

# STG_SHEET
# Generic function to load a google sheet and chosen columns into staging
def stg_sheet(sheet_name, columns_list):
    
    print(f'Running {inspect.stack()[0][3]}, {sheet_name}...')

    url = f'https://docs.google.com/spreadsheets/d/{data_config["dsnotes_sheet_id"]}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    df = pd.read_csv(url)[columns_list]

    with duckdb.connect(f'{data_config["data_directory"]}/{data_config["database_name"]}') as con:
        con.sql(f'create or replace table {data_config["schema_stg"]}.stg_{sheet_name} as select * from df')
    
    return df
