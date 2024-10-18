import duckdb
import os
from pipeline.read_raw import read_gpx, read_sheet
import pandas as pd


def stg_rides():

    df = []
    route_ids = set()

    files = os.listdir("data/gpx_files")
    for f in files:
        # Check if route already parsed
        route_id = f"{f.split('_in_')[1].split('.gpx')[0]}__{f.split('_on_')[1].split('_in_')[0]}"
        if route_id not in route_ids:
            data = read_gpx(f"data/gpx_files/{f}")
            df.append(data)
            route_ids.add(route_id)
        else:
            print(f"{route_id} already exists - can remove {f}") # could add remove file here but maybe not needed
            
    df = pd.concat(df, ignore_index=True)

    with duckdb.connect("data/data.duckdb") as con:
        con.sql(f"""CREATE OR REPLACE TABLE STAGING.stg_rides AS 
            SELECT 
                world, route, altitude, distance
            FROM df
            """)

    print("Loaded stg_rides")


def stg_sheet(sheet_name, columns_list):

    df = read_sheet(sheet_name, columns_list)

    with duckdb.connect("data/data.duckdb") as con:
        con.sql(f"""CREATE OR REPLACE TABLE STAGING.stg_{sheet_name} AS 
                SELECT *
                FROM df""")

    print(f"Loaded stg_{sheet_name}")