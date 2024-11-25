import duckdb
import streamlit as st
from new_pipeline.staging.stg_sheet import stg_sheet
from new_pipeline.staging.stg_rides import stg_rides
from new_pipeline.intermediate.int_routes import int_routes
from new_pipeline.intermediate.int_rides import int_rides
from new_pipeline.intermediate.int_notes import int_notes
from new_pipeline.core.dim_routes import dim_routes
from new_pipeline.core.dim_rides import dim_rides
from new_pipeline.core.dim_notes import dim_notes
import argparse

# Create the parser
parser = argparse.ArgumentParser(description='control which sections of the pipeline to run')

parser.add_argument('-r', action='store_true', help='Refresh rides gpx data')
parser.add_argument('-g', action='store_true', help='Refresh google data')
parser.add_argument('-i', action='store_true', help='Refresh intermediate data')
parser.add_argument('-c', action='store_true', help='Refresh core data')

args = parser.parse_args()

data_config = st.secrets['data_config']

# Create schema
with duckdb.connect(f'{data_config["data_directory"]}/{data_config["test_db"]}') as con:
    con.sql(f'create schema if not exists {data_config["schema_stg"]}')
    con.sql(f'create schema if not exists {data_config["schema_int"]}')
    con.sql(f'create schema if not exists {data_config["schema_prd"]}')

if args.g:
    stg_sheet('zi_routes', ['world', 'route', 'total', 'lead', 'restriction'])
    stg_sheet('routes', ['world','route', 'circuit','first_lap_whole','full_route_start','full_route_finish'])
    stg_sheet('sectors', ['sector_id', 'sector_start'])
    stg_sheet('notes', ['sector_id', 'note_title', 'note_start', 'note_end', 'note_type', 'note'])
    stg_sheet('waypoints', ['world', 'route', 'sector_id', 'sector_start'])

if args.r:
    stg_rides()

if args.i:
    int_routes()
    int_rides()
    int_notes()

if args.c:
    dim_routes()
    dim_rides()
    dim_notes()