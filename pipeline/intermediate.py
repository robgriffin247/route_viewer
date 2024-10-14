import duckdb
import os

# Much of the logic here is maybe better suited to core, but that's not important enough to move right now

def int_fits(verbose=False):
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
                            CONCAT(CAST(ROUND(CAST(altitude_met AS DECIMAL(10,1)), 1) as varchar), ' m') AS altitude_met_fmt,
                            CONCAT(CAST(ROUND(CAST(altitude_imp AS DECIMAL(10,1)), 1) as varchar), ' ft') AS altitude_imp_fmt
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
                        FROM CHANGE),
                    
                    FORMAT_GRADIENT AS (
                        SELECT *--,
                            --CONCAT(CAST(ROUND(CAST(gradient AS DECIMAL(10,1)), 1) as varchar), '%') AS gradient_fmt
                        FROM GRADIENT
                    )

                SELECT * EXCLUDE(distance_delta, altitude_delta) FROM FORMAT_GRADIENT""").to_df()
        
        con.sql(f"CREATE OR REPLACE TABLE {os.getenv('INT_SCHEMA')}.int_fits AS SELECT * FROM fit_df")

        if verbose:
            print(con.sql(f"SELECT * FROM {os.getenv('INT_SCHEMA')}.int_fits LIMIT 5"))

def int_notes(verbose=False):
    with duckdb.connect(f"{os.getenv('DB')}") as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('INT_SCHEMA')}")

        notes_df = con.sql(f"""
                            WITH SOURCE AS (
                                SELECT * FROM {os.getenv('STG_SCHEMA')}.stg_notes
                            ),

                            RENAME AS (
                                SELECT 
                                    world, route, 
                                    name AS segment,
                                    type,
                                    start AS start_km,
                                    "end" AS end_km,
                                    note AS notes
                                FROM SOURCE
                            ),

                            BLANKS AS (
                                SELECT * EXCLUDE(segment),
                                    CASE WHEN segment = LAG(segment) OVER() THEN '' ELSE segment END AS segment
                                FROM RENAME
                            ),

                            NUMERICS AS (
                                SELECT * EXCLUDE(start_km, end_km),
                                    TRY_CAST(REPLACE(start_km, ',', '.') AS FLOAT) AS start_km,
                                    TRY_CAST(REPLACE(end_km, ',', '.') AS FLOAT) AS end_km
                                    --TRY_CAST(REPLACE(from_met, ',', '.') AS FLOAT)/1.609344 AS from_imp, 
                                    --TRY_CAST(REPLACE(to_met, ',', '.') AS FLOAT)/1.609344 AS to_imp 
                                FROM BLANKS
                            )/*,

                            FORMATS AS (
                                SELECT *,
                                    CONCAT(CAST(ROUND(CAST(from_met AS DECIMAL(10,2)), 2) as varchar), ' km') AS from_met_fmt,
                                    CONCAT(CAST(ROUND(CAST(to_met AS DECIMAL(10,2)), 2) as varchar), ' km') AS to_met_fmt,
                                    CONCAT(CAST(ROUND(CAST(from_imp AS DECIMAL(10,2)), 2) as varchar), ' mi') AS from_imp_fmt,
                                    CONCAT(CAST(ROUND(CAST(to_imp AS DECIMAL(10,2)), 2) as varchar), ' mi') AS to_imp_fmt
                                FROM NUMERICS
                            )*/


                            
                            SELECT * FROM NUMERICS
                            """)
        
        con.sql(f"CREATE OR REPLACE TABLE {os.getenv('INT_SCHEMA')}.int_notes AS SELECT * FROM notes_df")

        if verbose:
            print(con.sql(f"SELECT * FROM {os.getenv('INT_SCHEMA')}.int_notes LIMIT 5"))
    

def int_routes(verbose=False):
    with duckdb.connect(f"{os.getenv('DB')}") as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('INT_SCHEMA')}")

        con.sql(f"""CREATE OR REPLACE TABLE {os.getenv('INT_SCHEMA')}.int_routes AS 
                    SELECT DISTINCT(world), route 
                    FROM {os.getenv('STG_SCHEMA')}.stg_fits 
                    GROUP BY world, route""")
        
        if verbose:
            print(con.sql(f"SELECT * FROM {os.getenv('INT_SCHEMA')}.int_routes LIMIT 5"))
