import pandas as pd

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
    world = file.split("_in_")[1].split(".gpx")[0].replace("_", " ")
    route = file.split("_on_")[1].split("_in_")[0].replace("_", " ")

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


    df["file"] = file
    df["world"] = world
    df["route"] = route
    
    return df[["world", "route", "distance", "altitude", "longitude", "latitude"]]

def read_sheet(sheet_name, columns_list, refresh=True):

    if not refresh:
        df = pd.read_csv(f"data/{sheet_name}.csv")

    else:
        sheet_id = "1qHMTUfpi9Gy_l3g9P4umsfdGaJ3O6Bdh9R1yNguoBEc"
        
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        df = pd.read_csv(url)[columns_list]
        df.to_csv(f"data/{sheet_name}.csv")
    
    return df

