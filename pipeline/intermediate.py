import duckdb
import os

def int_fits():
    with duckdb.connect(f"{os.getenv('DB')}") as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('INT_SCHEMA')}")

        fit_df = con.sql(f"""
                WITH 
                    SOURCE AS (SELECT * FROM {os.getenv('STG_SCHEMA')}.stg_fits),
                    
                    SELECT_COLS AS (
                        SELECT world, route, distance, altitude FROM SOURCE                      
                    ),

                    CONVERT AS (
                        SELECT world, route, distance, altitude,
                            distance/1000 AS distance_met,
                            distance/1609.344 AS distance_imp,
                            altitude AS altitude_met,
                            altitude/0.3048 AS altitude_imp
                        FROM SOURCE
                    ),

                    FORMAT AS (
                        SELECT *,
                            CONCAT(CAST(ROUND(CAST(distance_met AS DECIMAL(10,2)), 2) as varchar), ' km') AS distance_met_fmt,
                            CONCAT(CAST(ROUND(CAST(distance_imp AS DECIMAL(10,2)), 2) as varchar), ' miles') AS distance_imp_fmt,
                            CONCAT(CAST(ROUND(CAST(altitude_met AS DECIMAL(10,2)), 2) as varchar), ' m') AS altitude_met_fmt,
                            CONCAT(CAST(ROUND(CAST(altitude_imp AS DECIMAL(10,2)), 2) as varchar), ' ft') AS altitude_imp_fmt
                        FROM CONVERT
                    ),

                    CHANGE AS (
                        SELECT *,
                            CASE WHEN ROW_NUMBER() OVER() = 1 THEN 0 ELSE distance - LAG(distance) OVER() END AS distance_delta,
                            CASE WHEN ROW_NUMBER() OVER() = 1 THEN 0 ELSE altitude - LAG(altitude) OVER() END AS altitude_delta
                        FROM FORMAT),

                    GRADIENT AS (
                        SELECT *,
                            CASE WHEN ROW_NUMBER() OVER() = 1 THEN 0 ELSE altitude_delta/distance_delta*100 END AS gradient
                        FROM CHANGE)

                SELECT * EXCLUDE(distance_delta, altitude_delta) FROM GRADIENT""").to_df()
        
        con.sql(f"CREATE OR REPLACE TABLE {os.getenv('INT_SCHEMA')}.int_fits AS SELECT * FROM fit_df")

        print(con.sql(f"SELECT * FROM {os.getenv('INT_SCHEMA')}.int_fits LIMIT 50"))

def int_notes():
    print("generating int_notes")
    # Cast string to decimal:
    # --TRY_CAST(REPLACE("start", ',', '.') AS FLOAT) as from_km,


def int_routes():
    print("generating int_routes")