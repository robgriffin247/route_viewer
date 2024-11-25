import duckdb
import streamlit as st
from pipeline.staging import stg_sheet, stg_rides
from pipeline.intermediate import int_routes, int_rides, int_sectors, int_sector_descriptions, int_route_sectors
from pipeline.core import dim_rides, dim_notes, dim_routes

data_config = st.secrets["data_config"]

import argparse

# Create the parser
parser = argparse.ArgumentParser(description='control which sections of the pipeline to run')

parser.add_argument('-stg', action='store_true', help='Run staging')
parser.add_argument('-google', action='store_true', help='Run staging; Google only')
parser.add_argument('-int', action='store_true', help='Run intermediate')
parser.add_argument('-core', action='store_true', help='Run core')
parser.add_argument('-summary', action='store_true', help='Run summary')

args = parser.parse_args()

if not (args.stg or args.google or args.int or args.core or args.summary):
    args.stg = True
    args.google = True
    args.int = True
    args.core = True

if args.stg or args.google:
    print("Running staging...")
    #with duckdb.connect(f'{os.getenv("data_dir")}/{os.getenv("database")}') as con:
    with duckdb.connect(f'{data_config["data_directory"]}/{data_config["database_name"]}') as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS STAGING")

    stg_sheet("routes", ["Map", "Route", "Length", "Lead-In", "Restriction"])
    stg_sheet("route_lengths", ["world", "route", "lead", "total", "circuit", "complete_notes"])
    stg_sheet("sectors", ["world", "sector_id", "sector_start_landmark", "sector_start_point", "sector_description"])
    stg_sheet("sector_descriptions", ["world", "sector_id", "note_name", "note_start_km", "note_end_km", "note_type", "note_description"])
    stg_sheet("route_sectors", ["world", "route", "sector_id", "sector_start"])

if args.stg:
    stg_rides()


if args.int:
    print("Running intermediate...")
    with duckdb.connect(f'{data_config["data_directory"]}/{data_config["database_name"]}') as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS INTERMEDIATE")
    
    int_routes()
    int_rides()
    int_sectors()
    int_sector_descriptions()
    int_route_sectors()


if args.core:
    print("Running core...")
    with duckdb.connect(f'{data_config["data_directory"]}/{data_config["database_name"]}') as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS CORE")
    
    dim_rides()
    dim_notes()
    dim_routes()

if args.summary:
    with duckdb.connect(f'{data_config["data_directory"]}/{data_config["database_name"]}') as con:
        print('=' * 80 + '\n' + 'Tables')
        print(con.sql(f"SHOW ALL TABLES"))
    

        print('=' * 80 + '\n' + 'GPX coverage: files needed for...')
        print(con.sql(f"""
                      with rides as (
                        select distinct(world, route) as route from core.dim_rides
                      ),
                      routes as (
                        select 
                            distinct(map, route) as route,
                            case when restriction like '%Run%' then FALSE else TRUE end as ride
                        from staging.stg_routes 
                      )
                      
                      select route from routes where route not in (select route from rides) and ride
                      """))
