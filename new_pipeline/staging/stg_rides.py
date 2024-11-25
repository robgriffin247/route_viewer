import duckdb
import streamlit as st
import pandas as pd
import os 
import gpxpy
import geopy.distance
import inspect

# Setup database names and locations
data_config = st.secrets['data_config']

# STG_RIDES
# Reads data from GPX files into a single table of ride data for all routes (long, lat, distance and elevation)
def stg_rides():

    print(f'Running {inspect.stack()[0][3]}...')
    
    df = []
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

            row_data = pd.DataFrame.from_records(points)

            coords = [(p.latitude, p.longitude) for p in row_data.itertuples()]
            row_data['distance_delta'] = [0] + [geopy.distance.distance(from_, to).m for from_, to in zip(coords[:-1], coords[1:])]
            row_data['distance'] = row_data.distance_delta.cumsum()

            row_data['file'] = file
            row_data['world'] = world
            row_data['route'] = route

            df.append(row_data)
        else:
            print(f"Already parsed {route_id} - remove {file_path}")
            
    df = pd.concat(df, ignore_index=True)

    df.to_csv(f'{data_config["data_directory"]}/rides.csv', index=False)

    with duckdb.connect(f'{data_config["data_directory"]}/{data_config["test_db"]}') as con:
        con.sql(f'CREATE OR REPLACE TABLE {data_config["schema_stg"]}.{inspect.stack()[0][3]} AS SELECT file, world, route, longitude, latitude, altitude, distance FROM df')

    return(df)