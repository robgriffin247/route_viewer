import duckdb
import os

def dim_fits(verbose=False):
    with duckdb.connect(f"{os.getenv('DB')}") as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('PRD_SCHEMA')}")

        con.sql(f"""CREATE OR REPLACE TABLE {os.getenv('PRD_SCHEMA')}.dim_fits AS
                    SELECT * 
                    FROM {os.getenv('INT_SCHEMA')}.int_fits""")

        if verbose:
            print(con.sql(f"SELECT * FROM {os.getenv('PRD_SCHEMA')}.dim_fits LIMIT 5"))


def dim_notes(verbose=False):
    with duckdb.connect(f"{os.getenv('DB')}") as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('PRD_SCHEMA')}")

        con.sql(f"""CREATE OR REPLACE TABLE {os.getenv('PRD_SCHEMA')}.dim_notes AS
                    SELECT * 
                    FROM {os.getenv('INT_SCHEMA')}.int_notes""")

        if verbose:
            print(con.sql(f"SELECT * FROM {os.getenv('PRD_SCHEMA')}.dim_notes LIMIT 5"))



def dim_routes(verbose=False):
    with duckdb.connect(f"{os.getenv('DB')}") as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('PRD_SCHEMA')}")

        con.sql(f"""CREATE OR REPLACE TABLE {os.getenv('PRD_SCHEMA')}.dim_routes AS
                    SELECT * 
                    FROM {os.getenv('INT_SCHEMA')}.int_routes""")

        if verbose:
            print(con.sql(f"SELECT * FROM {os.getenv('PRD_SCHEMA')}.dim_routes LIMIT 5"))


