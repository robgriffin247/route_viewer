import duckdb
import os

# Much of the logic here is maybe better suited to core, but that's not important enough to move right now

def int_fits():
    with duckdb.connect(os.getenv('DB')) as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('INT_SCHEMA')}")

        fit_df = con.sql(f"""
                WITH 
                    SOURCE AS (
                         SELECT world, route, altitude, distance 
                         FROM {os.getenv('STG_SCHEMA')}.stg_fits
                    ),

                    ADD_CHANGE AS (
                        SELECT world, route, altitude, distance,
                            CASE WHEN ROW_NUMBER() OVER() = 1 THEN 0 ELSE altitude - LAG(altitude) OVER() END AS altitude_delta,
                            CASE WHEN ROW_NUMBER() OVER() = 1 THEN 0 ELSE distance - LAG(distance) OVER() END AS distance_delta
                        FROM SOURCE),

                    ADD_GRADIENT AS (
                        SELECT world, route, altitude, distance,
                            CASE WHEN ROW_NUMBER() OVER() = 1 THEN 0 ELSE altitude_delta/distance_delta*100 END AS gradient
                        FROM ADD_CHANGE),
                    
                    ROLL_GRADIENT AS (
                        SELECT world, route, altitude, distance,
                            MEAN(gradient) OVER (ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING) AS gradient
                        FROM ADD_GRADIENT)

                SELECT world, route, altitude, distance, gradient FROM ROLL_GRADIENT""").to_df()
        
        con.sql(f"CREATE OR REPLACE TABLE {os.getenv('INT_SCHEMA')}.int_fits AS SELECT * FROM fit_df")



def int_notes():
    with duckdb.connect(os.getenv('DB')) as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('INT_SCHEMA')}")

        notes_df = con.sql(f"""
                            WITH SOURCE AS (
                                SELECT world, route, segment, type, start_km, end_km, note
                                FROM {os.getenv('STG_SCHEMA')}.stg_notes
                            ),

                            REMOVE_REPEAT_SEGMENTS AS (
                                SELECT world, route,
                                    CASE WHEN segment = LAG(segment) OVER() THEN '' ELSE segment END AS segment,
                                    type, start_km, end_km, note
                                FROM SOURCE
                            ),

                            KM_TO_NUMERIC AS (
                                SELECT world, route, segment, type,
                                    TRY_CAST(REPLACE(start_km, ',', '.') AS FLOAT) AS start_km,
                                    TRY_CAST(REPLACE(end_km, ',', '.') AS FLOAT) AS end_km,
                                    note
                                FROM REMOVE_REPEAT_SEGMENTS
                            )

                            SELECT * FROM KM_TO_NUMERIC
                            """)
        
        con.sql(f"CREATE OR REPLACE TABLE {os.getenv('INT_SCHEMA')}.int_notes AS SELECT * FROM notes_df")



def int_routes():
    with duckdb.connect(os.getenv('DB')) as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('INT_SCHEMA')}")

        df = con.sql(f"""WITH SOURCE AS(
                        SELECT DISTINCT(world), route,
                            CASE WHEN 'finish' IN type THEN false ELSE true END AS can_lap 
                        FROM {os.getenv('STG_SCHEMA')}.stg_notes
                        GROUP BY world, route, type)
                        
                        SELECT world, route, CASE WHEN COUNT(can_lap) >1 THEN false ELSE true END AS can_lap FROM SOURCE GROUP BY world, route""")
        
        con.sql(f"""CREATE OR REPLACE TABLE {os.getenv('INT_SCHEMA')}.int_routes AS 
                    SELECT *
                    FROM df""")
        