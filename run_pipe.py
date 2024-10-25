import duckdb
import os
from pipeline.staging import stg_sheet, stg_rides
from pipeline.intermediate import int_routes, int_rides, int_sector_descriptions, int_route_sectors
from pipeline.core import dim_rides, dim_notes, dim_routes
from dotenv import load_dotenv
load_dotenv()

import argparse

# Create the parser
parser = argparse.ArgumentParser(description='control which sections of the pipeline to run')

parser.add_argument('-s', action='store_true', help='Run staging')
parser.add_argument('-i', action='store_true', help='Run intermediate')
parser.add_argument('-c', action='store_true', help='Run core')

args = parser.parse_args()

if not (args.s or args.i or args.c):
    args.s = True
    args.i = True
    args.c = True

if args.s:
    print("Running staging...")
    with duckdb.connect(f'{os.getenv("data_dir")}/{os.getenv("database")}') as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS STAGING")

    stg_sheet("routes", ["Map", "Route", "Length", "Lead-In", "Restriction"])
    stg_sheet("route_lengths", ["world", "route", "lead", "total", "gpx_correction"])
    stg_sheet("sectors", ["world", "sector_id", "sector_start_landmark", "sector_description"])
    stg_sheet("sector_descriptions", ["world", "sector_id", "note_name", "note_start_km", "note_end_km", "note_type", "note_description"])
    stg_sheet("route_sectors", ["world", "route", "sector_id", "sector_start"])
    stg_rides()


if args.i:
    print("Running intermediate...")
    with duckdb.connect(f'{os.getenv("data_dir")}/{os.getenv("database")}') as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS INTERMEDIATE")
    
    int_routes()
    int_rides()
    int_sector_descriptions()
    int_route_sectors()


if args.c:
    print("Running core...")
    with duckdb.connect(f'{os.getenv("data_dir")}/{os.getenv("database")}') as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS CORE")
    
    dim_rides()
    dim_notes()
    dim_routes()
