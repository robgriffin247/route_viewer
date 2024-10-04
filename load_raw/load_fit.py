import fitdecode
import pandas as pd
import os
import duckdb

from dotenv import load_dotenv

load_dotenv('..')

def extract_fit(fit_file):   

    # Get world and route from filename
    world = fit_file.split("__")[0].replace("_", " ")
    route = fit_file.split("__")[1].replace("_", " ")

    print(world + " " + route)

    # Read the fit file into a dataframe
    data = []

    with fitdecode.FitReader(f"{os.getenv('FIT_DIR')}/{fit_file}.fit") as f:
    #with fitdecode.FitReader(f"data/fit_files/{fit_file}.fit") as f:
        for frame in f:
            if isinstance(frame, fitdecode.records.FitDataMessage):
                message = {}
                for field in frame.fields:
                    message[field.name] = frame.get_value(field.name)

                data.append(message)

    data = pd.DataFrame(data)

    data["world"] = world
    data["route"] = route

    #with duckdb.connect(os.getenv('RAW_DB')) as con:
    with duckdb.connect("data/raw_data.duckdb") as con:
        #con.sql(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('STG_SCHEMA')}")
        con.sql(f"CREATE SCHEMA IF NOT EXISTS staging")
        con.sql(f"""
                CREATE OR REPLACE TABLE staging.stg_{world}__{route} AS 
                SELECT world, route, position_lat, position_long, altitude, distance
                FROM data
                WHERE position_lat IS NOT NULL""")
        
extract_fit("Makuri_Islands__Country_to_Coastal")

#with duckdb.connect(os.getenv('RAW_DB')) as con:
with duckdb.connect("data/raw_data.duckdb") as con:
    print(con.sql("SHOW ALL TABLES").to_df())
    data = con.sql("SELECT * FROM staging.stg_makuri_islands__country_to_coastal").to_df()
    print(data)
