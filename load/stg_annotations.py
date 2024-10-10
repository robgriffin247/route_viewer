import duckdb
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()


def stg_annotations():
    #annotations = pd.read_csv("data/annotations.csv")
    import pandas as pd

    sheet_id = "1qHMTUfpi9Gy_l3g9P4umsfdGaJ3O6Bdh9R1yNguoBEc"
    sheet_name = "race_notes"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

    annotations = pd.read_csv(url)[["platform", "world", "route", "name", "type", "start", "end", "note"]]

    with duckdb.connect(os.getenv('DB')) as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS STAGING")
        con.sql(f"""CREATE OR REPLACE TABLE STAGING.STG_ANNOTATIONS AS 
                SELECT 
                    platform, world, route, name, type,
                    TRY_CAST(REPLACE("start", ',', '.') AS FLOAT) as "start",
                    TRY_CAST(REPLACE("end", ',', '.') AS FLOAT) as "end",
                    note               
                FROM annotations""")
        