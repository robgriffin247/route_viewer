import duckdb
import streamlit as st
from pipeline.staging.stg_sheet import stg_sheet
from pipeline.staging.stg_rides import stg_rides
from pipeline.intermediate.int_routes import int_routes
from pipeline.intermediate.int_rides import int_rides
from pipeline.intermediate.int_notes import int_notes
from pipeline.core.dim_routes import dim_routes
from pipeline.core.dim_rides import dim_rides
from pipeline.core.dim_notes import dim_notes
import argparse
import os

# Create the parser
parser = argparse.ArgumentParser(
    description="control which sections of the pipeline to run"
)

parser.add_argument("-r", action="store_true", help="Refresh rides gpx data")
parser.add_argument("-g", action="store_true", help="Refresh google data")
parser.add_argument("-i", action="store_true", help="Refresh intermediate data")
parser.add_argument("-c", action="store_true", help="Refresh core data")

args = parser.parse_args()

data_config = st.secrets["data_config"]

# Create schema
with duckdb.connect(
    f'{data_config["data_directory"]}/{data_config["database_name"]}'
) as con:
    con.sql(f'create schema if not exists {data_config["schema_stg"]}')
    con.sql(f'create schema if not exists {data_config["schema_int"]}')
    con.sql(f'create schema if not exists {data_config["schema_prd"]}')

if args.g:
    stg_sheet("zi_routes", ["world", "route", "total", "lead", "restriction"])
    stg_sheet(
        "routes",
        [
            "world",
            "route",
            "circuit",
            "first_lap_whole",
            "full_route_start",
            "full_route_finish",
            "complete",
        ],
    )
    stg_sheet("sectors", ["sector_id", "sector_start"])
    stg_sheet(
        "notes",
        ["sector_id", "note_title", "note_start", "note_end", "note_type", "note"],
    )
    stg_sheet("waypoints", ["world", "route", "sector_id", "sector_start"])

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


# left to laod gpx for:
with duckdb.connect(
    f'{data_config["data_directory"]}/{data_config["database_name"]}'
) as con:
    loaded = con.sql(
        """
        with 
            loaded as (select distinct(concat(world, ': ', route)) as route from core.dim_rides),
            routes as (select distinct(concat(world, ': ', route)) as route from intermediate.int_routes) 
        select * from routes  where route not in (select * from loaded) order by route
        """
    ).to_df()

    n_loaded = len(loaded)
    n_routes = len(con.sql("select * from intermediate.int_routes").to_df())

    if n_loaded > 0:
        print(f"{(60*'=')}\nProvide GPX files for:\n")
        i = 0
        for index, value in loaded.iterrows():
            i += 1
            print(
                f" - {value.item()}: https://zwiftinsider.com/route/{value.item().split(': ')[1].replace(' ', '-').lower()}"
            )
            if not i % 5:
                print("")

        print("")
        print(f"Routes loaded: {n_routes-n_loaded} of {n_routes}")
        print("")


def check_gpx_files():

    files = os.listdir(f'{data_config["data_directory"]}/gpx_files')

    with duckdb.connect(
        f'{data_config["data_directory"]}/{data_config["database_name"]}'
    ) as con:
        routes = con.sql("select world, route from intermediate.int_routes")

        print(60 * "=")

        for file in files:
            world, route = [
                i.replace("_", " ").replace(".gpx", "") for i in file.split("__")
            ]

            df = con.sql(
                f"select * from routes where world='{world}' and route='{route}'"
            ).to_df()

            if (len(df) == 0) & (
                file
                not in (
                    "Watopia__Watopias_Waistband.gpx",
                    "France__RGV.gpx",
                    "Yorkshire__Queens_Highway.gpx",
                    "Paris__Champs-Élysées.gpx",
                    "Watopia__Climbers_Gambit.gpx",
                )
            ):
                print(f"CHECK: {world}, {route}")


check_gpx_files()
