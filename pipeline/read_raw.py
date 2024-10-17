import pandas as pd
import os
import fitdecode
import gpxpy
import geopy.distance

def read_fit(file):   

    # Get world and route from filename
    world = file.split("__")[1]
    route = file.split("__")[2]

    # Read the fit file into a dataframe
    df = []

    with fitdecode.FitReader(file) as f:
        for frame in f:
            if isinstance(frame, fitdecode.records.FitDataMessage):
                message = {}
                for field in frame.fields:
                    message[field.name] = frame.get_value(field.name)

                df.append(message)

    df = pd.DataFrame(df)

    df["world"] = world.replace("_", " ")
    df["route"] = route.replace("_", " ")
    
    return df


def read_gpx(file):

    # Get world and route from filename
    world = file.split("__")[1]
    route = file.split("__")[2].replace(".gpx",""   )

    with open(file) as f:
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


    df["world"] = world.replace("_", " ")
    df["route"] = route.replace("_", " ")
    
    return df[["world", "route", "distance", "altitude", "longitude", "latitude"]]
