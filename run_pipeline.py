from pipeline.staging import stg_sheet, stg_rides
from pipeline.intermediate import int_rides, int_routes, int_notes, int_notesx
from pipeline.core import dim_rides, dim_notes, dim_notesx
from pipeline.checks import too_short, to_get
import duckdb

import argparse

# Create the parser
parser = argparse.ArgumentParser(description='control which sections of the pipeline to run')

# -a = all
# -s = staging
# -i = intermedite
# -p = prod/core
# -d = dev
# -c = checks
# -m = main (staging, intermediate, prod/core)

# Add flags
parser.add_argument('-a', action='store_true', help='Run the entire pipeline')
parser.add_argument('-s', action='store_true', help='Run staging')
parser.add_argument('-i', action='store_true', help='Run intermediate')
parser.add_argument('-p', action='store_true', help='Run prod/core')
parser.add_argument('-m', action='store_true', help='Run main')
parser.add_argument('-d', action='store_true', help='Run dev')
parser.add_argument('-c', action='store_true', help='Run checks')

# Parse the arguments
args = parser.parse_args()

if not (args.a or args.s or args.i or args.p or args.m or args.d or args.c):
    args.a = True

if (args.a or args.m):
    args.s = True
    args.i = True
    args.p = True

if (args.a):
    args.s = True
    args.i = True
    args.p = True
    args.d = True
    args.c = True

# Main ---------------------------------------------------------
with duckdb.connect("data/data.duckdb") as con:
    con.sql(f"CREATE SCHEMA IF NOT EXISTS STAGING")
    con.sql(f"CREATE SCHEMA IF NOT EXISTS INTERMEDIATE")
    con.sql(f"CREATE SCHEMA IF NOT EXISTS CORE")

if args.s:
    stg_rides()
    stg_sheet("notes", ["world", "route", "segment", "type", "start_km", "end_km", "note"])
    stg_sheet("zi_routes", ["Map", "Route", "Length", "Elevation", "Lead-In", "Restriction", "ovr_lead", "ovr_total"])

if args.i:
    int_rides()
    int_routes()
    int_notes()

if args.p:
    dim_rides()
    dim_notes()


# DEV - this will replace notes later (stg_notes = stg_road_descriptions and stg_route_roads; *_notes=*_notesx)
if args.d:
    #stg_rides()
    stg_sheet("road_descriptions", ["world", "road", "sector_name", "sector_start", "sector_end", "sector_notes", "sector_type"])
    stg_sheet("route_roads", ["world", "route", "road", "start"])
    #stg_sheet("zi_routes", ["Map", "Route", "Length", "Elevation", "Lead-In", "Restriction"])

    int_notesx()
    #int_rides()
    #int_routes()

    dim_notesx()
    #dim_rides()

    with duckdb.connect("data/data.duckdb") as con:
        print(con.sql("SELECT * FROM CORE.dim_notesx"))

# CHECKS 
if args.c:
    too_short()
    to_get()


    # currently fixing new notes system - added ovr_lead and ovr_total; tweaking route notes; union on notesx and notes