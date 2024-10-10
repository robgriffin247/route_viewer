import duckdb
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

def dim_annotations():
    with duckdb.connect(os.getenv('DB')) as con:
        annotations_data = con.sql("""SELECT * FROM STAGING.STG_ANNOTATIONS""").to_df()

        con.sql("""CREATE SCHEMA IF NOT EXISTS CORE""")
        con.sql("""CREATE OR REPLACE TABLE CORE.DIM_ANNOTATIONS AS SELECT * FROM annotations_data ORDER BY platform, world, route, start""")

