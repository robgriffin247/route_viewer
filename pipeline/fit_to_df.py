import fitdecode
import pandas as pd
import os

def fit_to_df(fit_file):   

    # Get world and route from filename
    world = fit_file.split("__")[1]
    route = fit_file.split("__")[2]
    ride_date = fit_file.split("__")[3]

    # Read the fit file into a dataframe
    data = []

    with fitdecode.FitReader(f"{os.getenv('FIT_DIR')}/{fit_file}.fit") as f:
        for frame in f:
            if isinstance(frame, fitdecode.records.FitDataMessage):
                message = {}
                for field in frame.fields:
                    message[field.name] = frame.get_value(field.name)

                data.append(message)

    data = pd.DataFrame(data)

    data["world"] = world.replace("_", " ")
    data["route"] = route.replace("_", " ")
    data["ride_date"] = ride_date
    
    return data