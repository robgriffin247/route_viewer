import duckdb
import os
from dotenv import load_dotenv
from load_raw.fit_to_df import fit_to_df
import pandas as pd

load_dotenv()

def load_obt():
    obt = []

    files = os.listdir(f"{os.getenv('FIT_DIR')}")
    for f in files:
        data = fit_to_df(f.replace(".fit", ""))
        obt.append(data)

    obt = pd.concat(obt, ignore_index=True)
        
    with duckdb.connect(os.getenv('DB')) as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('INT_SCHEMA')}")
        con.sql(f"""CREATE OR REPLACE TABLE {os.getenv('INT_SCHEMA')}.obt_fit AS 
            SELECT world, route, position_lat, position_long, altitude, distance
            FROM obt 
            WHERE position_lat IS NOT NULL""")