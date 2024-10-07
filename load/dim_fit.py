import duckdb
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

def dim_fit():
    with duckdb.connect(os.getenv('DB')) as con:
        fit_data = con.sql("""SELECT * FROM STAGING.STG_FIT""").to_df()

        con.sql("""CREATE SCHEMA IF NOT EXISTS CORE""")
        con.sql("""CREATE OR REPLACE TABLE CORE.DIM_FIT AS SELECT * FROM fit_data""")

