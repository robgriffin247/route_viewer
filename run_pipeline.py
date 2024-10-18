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
    
    too_short = con.sql("""
                  WITH NOTES AS (
                    SELECT * FROM INTERMEDIATE.int_notes WHERE type in ('finish', 'lap_banner') 
                  ),
                  RIDES AS (
                    SELECT route_id, MAX(distance)/1000 AS total 
                    FROM INTERMEDIATE.int_rides
                    GROUP BY route_id
                  ),
                  TOO_SHORT AS (
                    SELECT RIDES.route_id, RIDES.total, NOTES.end_point
                    FROM RIDES LEFT JOIN NOTES ON RIDES.route_id=NOTES.route_id
                    WHERE RIDES.total < NOTES.end_point
                  )
                  SELECT * 
                  FROM TOO_SHORT
                  """)

    print("The following gpx files did not cover the entire route - remove them and find a new source:")
    print(too_short)
    print("="*80)
    print(" "*80)

    to_do = con.sql("""
            WITH ROUTES AS (
                SELECT route_id, world, route, total_length FROM INTERMEDIATE.int_routes WHERE ride
            ),
            ROUTES_RIDDEN AS (
                SELECT DISTINCT(route_id) AS route_id
                FROM INTERMEDIATE.int_rides
            )
            SELECT world, route FROM ROUTES WHERE route_id NOT IN (SELECT route_id FROM ROUTES_RIDDEN) ORDER BY total_length
            """)
    print("The following routes need gpx files:")
    print(to_do)
    print("="*80)
    print(" "*80)