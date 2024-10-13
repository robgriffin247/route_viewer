import duckdb
import os

def dim_fits(verbose=False):
    with duckdb.connect(os.getenv('DB')) as con:

        fits = con.sql(f"""
                WITH FITS AS (
                    SELECT * FROM {os.getenv('INT_SCHEMA')}.int_fits
                ),

                STARTS AS (
                    SELECT world, route, end_km FROM {os.getenv('INT_SCHEMA')}.int_notes WHERE type='lead'
                ),

                ENDS AS (
                    SELECT world, route, end_km FROM {os.getenv('INT_SCHEMA')}.int_notes WHERE type='finish'
                ),

                LEAD_ZONE AS (
                    SELECT FITS.*, 
                        CASE WHEN STARTS.end_km>=FITS.distance_met THEN 'leadin' ELSE 'lap' END AS zone
                    FROM FITS LEFT JOIN STARTS ON FITS.world=STARTS.world AND FITS.route=STARTS.route 
                ),

                FINISH_LINE_CUT AS (
                    SELECT L.* 
                    FROM LEAD_ZONE AS L LEFT JOIN ENDS AS E ON L.world=E.world AND L.route=E.route
                    WHERE E.end_km>=L.distance_met
                )

                SELECT * FROM FINISH_LINE_CUT

                """).to_df()

        con.sql(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('PRD_SCHEMA')}")

        con.sql(f"""CREATE OR REPLACE TABLE {os.getenv('PRD_SCHEMA')}.dim_fits AS
                    SELECT * 
                    FROM fits""")

        if verbose:
            print(con.sql(f"SELECT * FROM {os.getenv('PRD_SCHEMA')}.dim_fits LIMIT 5"))


def dim_notes(verbose=False):
    with duckdb.connect(os.getenv('DB')) as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('PRD_SCHEMA')}")

        con.sql(f"""CREATE OR REPLACE TABLE {os.getenv('PRD_SCHEMA')}.dim_notes AS
                    SELECT * 
                    FROM {os.getenv('INT_SCHEMA')}.int_notes""")

        if verbose:
            print(con.sql(f"SELECT * FROM {os.getenv('PRD_SCHEMA')}.dim_notes LIMIT 5"))



def dim_routes(verbose=False):
    with duckdb.connect(os.getenv('DB')) as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('PRD_SCHEMA')}")

        con.sql(f"""CREATE OR REPLACE TABLE {os.getenv('PRD_SCHEMA')}.dim_routes AS
                    SELECT * 
                    FROM {os.getenv('INT_SCHEMA')}.int_routes""")

        if verbose:
            print(con.sql(f"SELECT * FROM {os.getenv('PRD_SCHEMA')}.dim_routes LIMIT 5"))


