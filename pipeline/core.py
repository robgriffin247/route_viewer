import duckdb
import os

def dim_fits():
    with duckdb.connect(os.getenv('DB')) as con:

        fits = con.sql(f"""
                WITH SOURCE AS (
                    SELECT world, route, altitude, distance, gradient 
                    FROM {os.getenv('INT_SCHEMA')}.int_fits
                ),

                NOTES AS (
                    SELECT world, route, end_km*1000 AS end_km, type
                    FROM {os.getenv('INT_SCHEMA')}.int_notes
                ),

                LEAD_END AS (
                    SELECT world, route, end_km FROM NOTES WHERE type='lead'
                ),

                LAP_END AS (
                    SELECT world, route, end_km FROM NOTES WHERE type='finish'
                ),

                -- 0=lead, 1=main    
                ADD_LAP AS ( 
                    SELECT S.world, S.route, S.altitude, S.distance, S.gradient, 
                        CASE WHEN L.end_km>=S.distance THEN 0 ELSE 1 END AS lap
                    FROM SOURCE AS S LEFT JOIN LEAD_END AS L ON S.world=L.world AND S.route=L.route 
                ),

                CUT_TO_FINISH AS (
                    SELECT A.world, A.route, A.lap, A.altitude, A.distance, A.gradient
                    FROM ADD_LAP AS A LEFT JOIN LAP_END AS L ON A.world=L.world AND A.route=L.route
                    WHERE L.end_km>=A.distance
                )

                SELECT world, route, lap, altitude, distance, gradient 
                FROM CUT_TO_FINISH

                """).to_df()

        con.sql(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('PRD_SCHEMA')}")

        con.sql(f"""CREATE OR REPLACE TABLE {os.getenv('PRD_SCHEMA')}.dim_fits AS
                    SELECT * 
                    FROM fits""")


def dim_notes():
    with duckdb.connect(os.getenv('DB')) as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('PRD_SCHEMA')}")

        con.sql(f"""CREATE OR REPLACE TABLE {os.getenv('PRD_SCHEMA')}.dim_notes AS
                    SELECT * 
                    FROM {os.getenv('INT_SCHEMA')}.int_notes""")


def dim_routes():
    with duckdb.connect(os.getenv('DB')) as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('PRD_SCHEMA')}")

        con.sql(f"""CREATE OR REPLACE TABLE {os.getenv('PRD_SCHEMA')}.dim_routes AS
                    SELECT * 
                    FROM {os.getenv('INT_SCHEMA')}.int_routes""")
