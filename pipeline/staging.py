import duckdb
import os
import streamlit as st
import pandas as pd
import gpxpy
import geopy.distance

data_config = st.secrets["data_config"]

with duckdb.connect(f'{data_config["data_directory"]}/{data_config["database_name"]}') as con:
    con.sql(f'CREATE SCHEMA IF NOT EXISTS STAGING')
    con.sql(f'CREATE SCHEMA IF NOT EXISTS INTERMEDIATE')
    con.sql(f'CREATE SCHEMA IF NOT EXISTS CORE')

# Generic function to stage a given sheet and [columns]
def stg_sheet(sheet_name, columns_list, refresh=True):

    if not refresh:
        df = pd.read_csv(f'{data_config["data_directory"]}/{sheet_name}.csv')

    else:
        url = f'https://docs.google.com/spreadsheets/d/{data_config["google_sheet_id"]}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
        df = pd.read_csv(url)[columns_list]
        df.to_csv(f'{data_config["data_directory"]}/{sheet_name}.csv')
    
    with duckdb.connect(f'{data_config["data_directory"]}/{data_config["database_name"]}') as con:
        con.sql(f'CREATE OR REPLACE TABLE STAGING.stg_{sheet_name} AS SELECT * FROM df')


# Function to read the gpx files into the database
def stg_rides():
    data = []
    files = os.listdir(f'{data_config["data_directory"]}/gpx_files')
    route_ids = set()

    for file in files:
        world, route = [i.replace("_", " ").replace(".gpx", "") for i in file.split("__")]

        route_id = f"{world.replace('_', ' ')}__{route.replace('_', ' ')}"
        if route_id not in route_ids:
            route_ids.add(route_id)

            file_path = f'{data_config["data_directory"]}/gpx_files/{file}'

            with open(file_path) as f:
                gpx = gpxpy.parse(f)
            
            points = []

            for segment in gpx.tracks[0].segments:
                for p in segment.points:
                    points.append({
                        'latitude': p.latitude,
                        'longitude': p.longitude,
                        'altitude': p.elevation,
                    })

            df = pd.DataFrame.from_records(points)

            coords = [(p.latitude, p.longitude) for p in df.itertuples()]
            df['distance_delta'] = [0] + [geopy.distance.distance(from_, to).m for from_, to in zip(coords[:-1], coords[1:])]
            df['distance'] = df.distance_delta.cumsum()

            df['file'] = file
            df['world'] = world
            df['route'] = route

            data.append(df)
        else:
            print(f"Already parsed {route_id} - remove {file_path}")
            
    data = pd.concat(data, ignore_index=True)

    with duckdb.connect(f'{data_config["data_directory"]}/{data_config["database_name"]}') as con:
        con.sql(f'CREATE OR REPLACE TABLE STAGING.stg_rides AS SELECT file, world, route, longitude, latitude, altitude, distance FROM data')
