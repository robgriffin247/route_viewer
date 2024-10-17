import gpxpy
import pandas as pd
import geopy.distance
import os 


def read_gpx(file):
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

    return df[["distance", "altitude", "longitude", "latitude"]]
