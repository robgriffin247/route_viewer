import duckdb
import os
from dotenv import load_dotenv
from load.fit_to_df import fit_to_df
import pandas as pd

load_dotenv()

def stg_fit():
    data = []

    files = os.listdir(f"{os.getenv('FIT_DIR')}")
    for f in files:
        data.append(fit_to_df(f.replace(".fit", "")))

    data = pd.concat(data, ignore_index=True)

    with duckdb.connect(os.getenv('DB')) as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS STAGING")
        con.sql(f"""CREATE OR REPLACE TABLE STAGING.STG_FIT AS 
            SELECT platform, world, route, position_lat, position_long, altitude, distance
            FROM data 
            WHERE position_lat IS NOT NULL""")
