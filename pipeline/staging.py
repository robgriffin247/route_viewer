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


def stg_notes(refresh=False):
    if not refresh:
        notes = pd.read_csv("data/notes.csv")

    else:
        sheet_id = "1qHMTUfpi9Gy_l3g9P4umsfdGaJ3O6Bdh9R1yNguoBEc"
        sheet_name = "race_notes"
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

        notes = pd.read_csv(url)[["world", "route", "segment", "type", "start_km", "end_km", "note"]]

        notes.to_csv("data/notes.csv")

    with duckdb.connect(os.getenv('DB')) as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('STG_SCHEMA')}")

        con.sql(f"""CREATE OR REPLACE TABLE {os.getenv('STG_SCHEMA')}.stg_notes AS 
                SELECT world, route, segment, type, start_km, end_km, note
                FROM notes""")
