import duckdb
import os
from pipeline.read_raw import read_gpx, read_sheet
import pandas as pd


def stg_rides():

    df = []

    files = os.listdir("data/gpx_files")
    for f in files:
        df.append(read_gpx(f"data/gpx_files/{f}"))

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