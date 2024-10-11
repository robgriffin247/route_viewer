import duckdb
import os

def int_fits():
    with duckdb.connect(f"{os.getenv('DB')}") as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('INT_SCHEMA')}")

        fit_df = con.sql(f"""
                WITH SOURCE AS (SELECT * FROM {os.getenv('STG_SCHEMA')}.stg_fits),
                SELECT_COLS AS (
                    SELECT world, route, distance, altitude FROM SOURCE                      
                ),
                CONVERT AS (
                    SELECT *,
                        distance/1000 AS distance_km,
                        distance/1609.344 AS distance_miles,
                        altitude/0.3048 AS altitude_ft
                    FROM SOURCE
                ),
                FORMAT AS (
                    SELECT *
                    FROM CONVERT
                ),
                CHANGE AS (
                    SELECT * 
                    FROM FORMAT),
                GRADIENT AS (
                    SELECT *
                    FROM CHANGE)

                SELECT * FROM GRADIENT""").to_df()
        
        con.sql(f"CREATE OR REPLACE TABLE {os.getenv('INT_SCHEMA')}.int_fits AS SELECT * FROM fit_df")

        print(con.sql(f"SELECT * FROM {os.getenv('INT_SCHEMA')}.int_fits LIMIT 5"))

def int_notes():
    print("generating int_notes")
    # Cast string to decimal:
    # --TRY_CAST(REPLACE("start", ',', '.') AS FLOAT) as from_km,


def int_routes():
    print("generating int_routes")