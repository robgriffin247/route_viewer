from pipeline.staging import stg_sheet, stg_rides
from pipeline.intermediate import int_rides, int_routes, int_notes
from pipeline.core import dim_rides, dim_notes
import duckdb


with duckdb.connect("data/data.duckdb") as con:
    con.sql(f"CREATE SCHEMA IF NOT EXISTS STAGING")
    con.sql(f"CREATE SCHEMA IF NOT EXISTS INTERMEDIATE")
    con.sql(f"CREATE SCHEMA IF NOT EXISTS CORE")

"""
"""
stg_rides()
stg_sheet("notes", ["world", "route", "segment", "type", "start_km", "end_km", "note"])
stg_sheet("zi_routes", ["Map", "Route", "Length", "Elevation", "Lead-In", "Restriction"])

int_rides()
int_routes()
int_notes()

dim_rides()
dim_notes()

with duckdb.connect("data/data.duckdb") as con:
    
    print(con.sql("SELECT * FROM STAGING.stg_notes" ))
    print(con.sql("SELECT * FROM INTERMEDIATE.int_notes" ))
    print(con.sql("SELECT * FROM CORE.dim_notes" ))
    #print(con.sql("SHOW ALL TABLES"))