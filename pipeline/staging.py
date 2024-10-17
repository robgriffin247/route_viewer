import duckdb
import os
from dotenv import load_dotenv
from pipeline.read_raw import read_fit, read_gpx
import pandas as pd

def stg_fits():

    df = []

    files = os.listdir("data/fit_files")
    for f in files:
        df.append(read_fit(f"data/fit_files/{f}"))

    df = pd.concat(df, ignore_index=True)

    with duckdb.connect(os.getenv('DB')) as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('STG_SCHEMA')}")

        con.sql(f"""CREATE OR REPLACE TABLE {os.getenv('STG_SCHEMA')}.stg_fits AS 
            SELECT world, route, altitude, distance
            FROM df 
            WHERE position_lat IS NOT NULL""")

def stg_rides():

    df = []

    files = os.listdir("data/gpx_files")
    for f in files:
        df.append(read_gpx(f"data/gpx_files/{f}"))

    df = pd.concat(df, ignore_index=True)

    with duckdb.connect(os.getenv('DB')) as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('STG_SCHEMA')}")

        con.sql(f"""CREATE OR REPLACE TABLE {os.getenv('STG_SCHEMA')}.stg_rides AS 
            SELECT world, route, altitude, distance
            FROM df
            """)

        print(con.sql("SELECT * FROM STAGING.stg_rides"))

def stg_sheets(refresh=False):
    if not refresh:
        notes = pd.read_csv("data/notes.csv")
        routes = pd.read_csv("data/routes.csv")

    else:
        sheet_id = "1qHMTUfpi9Gy_l3g9P4umsfdGaJ3O6Bdh9R1yNguoBEc"
        
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=notes"
        notes = pd.read_csv(url)[["world", "route", "segment", "type", "start_km", "end_km", "note"]]
        notes.to_csv("data/notes.csv")

        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=routes"
        routes = pd.read_csv(url)[["world", "route", "fit", "basic", "complete", "can_lap", "priority"]]
        routes.to_csv("data/routes.csv")
        
        #url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=zp_races"
        #races = pd.read_csv(url)[["route"]]
        #print(races["route"].value_counts()[21:40])
        

    with duckdb.connect(os.getenv('DB')) as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('STG_SCHEMA')}")

        con.sql(f"""CREATE OR REPLACE TABLE {os.getenv('STG_SCHEMA')}.stg_notes AS 
                SELECT world, route, segment, type, start_km, end_km, note
                FROM notes""")

        con.sql(f"""CREATE OR REPLACE TABLE {os.getenv('STG_SCHEMA')}.stg_routes AS 
                SELECT world, route, fit, basic, complete, can_lap, priority
                FROM routes""")

