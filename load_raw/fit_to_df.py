import fitdecode
import pandas as pd
import os
import duckdb

def fit_to_df(fit_file):   

    # Get world and route from filename
    platform = fit_file.split("__")[0]
    world = fit_file.split("__")[1]
    route = fit_file.split("__")[2]

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

    # Add world and route to allow use of one-big-table (OBT) later
    data["platform"] = platform.replace("_", " ")
    data["world"] = world.replace("_", " ")
    data["route"] = route.replace("_", " ")

    return data