import duckdb
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()


def stg_annotations():
    annotations = pd.read_csv("data/annotations.csv")
    with duckdb.connect(os.getenv('DB')) as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS STAGING")
        con.sql(f"""CREATE OR REPLACE TABLE STAGING.STG_ANNOTATIONS AS 
                SELECT * 
                FROM annotations""")