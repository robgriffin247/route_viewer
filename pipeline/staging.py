import duckdb
import os
from dotenv import load_dotenv
from pipeline.fit_to_df import fit_to_df
import pandas as pd

def stg_fits():

    data = []

    files = os.listdir(os.getenv('FIT_DIR'))
    for f in files:
        data.append(fit_to_df(f.replace(".fit", "")))

    data = pd.concat(data, ignore_index=True)

    with duckdb.connect(os.getenv('DB')) as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('STG_SCHEMA')}")

        con.sql(f"""CREATE OR REPLACE TABLE {os.getenv('STG_SCHEMA')}.stg_fits AS 
            SELECT world, route, altitude, distance
            FROM data 
            WHERE position_lat IS NOT NULL""")


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

