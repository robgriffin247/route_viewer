import duckdb
import streamlit as st 
import numpy as np 
import pandas as pd

data_config = st.secrets["data_config"]

def route_input():
    # Set layout
    world, route = st.columns([4,6])

    # Get the routes that have been desribed
    with duckdb.connect(f'{data_config["data_dir"]}/{data_config["database"]}') as con:
        available_routes = con.sql("SELECT DISTINCT(world) AS world, route FROM CORE.dim_notes ORDER BY world, route").to_df()

    # User input for world
    world.selectbox("World", 
                    label_visibility="hidden",
                    index=int(np.where(available_routes.world.unique()=="Watopia")[0][0]),
                    options=available_routes.world.unique(),
                    key="world")
    
    # User input for route filtered on world
    route.selectbox("Route", 
                    label_visibility="hidden", 
                    options=available_routes.route[available_routes.world==st.session_state["world"]],
                    key="route")
    
    # Get the data for the route (ride = .gpx data used for plotting; note = notes for the route; route = route metadata such as length, lead in)
    with duckdb.connect(f'{data_config["data_dir"]}/{data_config["database"]}') as con:
        st.session_state["ride_data"] = con.sql(f"""
                        SELECT * FROM CORE.dim_rides WHERE world='{st.session_state["world"]}' AND route='{st.session_state["route"]}'
                        """).to_df()  
        
        st.session_state["note_data"] = con.sql(f"""
                SELECT *, CASE WHEN type!='other' THEN true ELSE false END AS highlight
                FROM CORE.dim_notes WHERE world='{st.session_state["world"]}' AND route='{st.session_state["route"]}'
                """).to_df()  
    
        st.session_state["route_data"] = con.sql(f"""
                SELECT * FROM CORE.dim_routes WHERE world='{st.session_state["world"]}' AND route='{st.session_state["route"]}'
                """).to_df()

def controls_input():
    # Set layout
    laps, metric, _= st.columns([4,3,6], vertical_alignment="bottom")

    # LAPPING ----------------------------
    # Control for circuit - if the route starts/finishes in different locations, it cannot be lapped so limit to 1
    if st.session_state["route_data"].loc[0, "circuit"]:
        laps.number_input("Laps", value=1, min_value=1, max_value=20, key="laps")
    else:
        laps.number_input("Laps", value=1, min_value=1, max_value=1, key="laps", help="It is not possible to lap this route - the start and finish banners are in different locations!")

    # Subset note data to length of ride - some routes will finish part way through a decribed sector
    ride_length = st.session_state["ride_data"]["distance"].max()
    st.session_state["note_data"] = st.session_state["note_data"].loc[st.session_state["note_data"]["start_point"]<=ride_length]

    # Repeat data for lapping (get main lap data/not lead in, then repeat)
    lead_length=[float(i) for i in st.session_state["route_data"]["lead"]][0]
    lap_length=[float(i) for i in st.session_state["route_data"]["lap"]]
    lap_note_data = st.session_state["note_data"].loc[st.session_state["note_data"]["start_point"] >= lead_length]
    lap_ride_data = st.session_state["ride_data"].loc[st.session_state["ride_data"]["lap"]==1]
    
    for lap in range(1, st.session_state["laps"]):
        lap_note_data.loc[:, "start_point"] += lap_length
        lap_note_data.loc[:, "end_point"] += lap_length
        lap_ride_data.loc[:, "distance"] += lap_length
        st.session_state["note_data"] = pd.concat([st.session_state["note_data"], lap_note_data], ignore_index=True)
        st.session_state["ride_data"] = pd.concat([st.session_state["ride_data"], lap_ride_data], ignore_index=True)

    # Clean up
    st.session_state["ride_data"] = st.session_state["ride_data"].sort_values(by=["world", "route", "distance"])
    
    st.session_state["note_data"] = st.session_state["note_data"].sort_values(by=["world", "route", "start_point", "type", "segment", "end_point"],
                                                                              ascending=[True, True, True, True, True, False])

    # METRIC ---------------------------
    metric.toggle("Metric",
                value=True,
                key="metric")

    # Create modifiers
    if st.session_state["metric"]:
        st.session_state["units"] = {"distance":"km", "altitude":"m"}
        st.session_state["scales"] = {"distance":1.0, "altitude":1.0}
    else:
        st.session_state["units"] = {"distance":"mi", "altitude":"ft"}
        st.session_state["scales"] = {"distance":0.621371192, "altitude":3.2808399}

    # Modify data
    st.session_state["ride_data"]["distance"] = st.session_state["ride_data"]["distance"] * st.session_state["scales"]["distance"]
    st.session_state["ride_data"]["altitude"] = st.session_state["ride_data"]["altitude"] * st.session_state["scales"]["altitude"]

    st.session_state["note_data"]["start_point"] = st.session_state["note_data"]["start_point"] * st.session_state["scales"]["distance"]
    st.session_state["note_data"]["end_point"] = st.session_state["note_data"]["end_point"] * st.session_state["scales"]["distance"]
    
    st.session_state["ride_data"]["distance_tip"] = [f"{'{:.2f}'.format(round(d,2))} {st.session_state['units']['distance']}" for d in st.session_state["ride_data"]["distance"]] 
    st.session_state["ride_data"]["altitude_tip"] = [f"{'{:.1f}'.format(round(d,1))} {st.session_state['units']['altitude']}" for d in st.session_state["ride_data"]["altitude"]] 
    st.session_state["ride_data"]["gradient_tip"] = [f"{'{:.1f}'.format(round(d,1))}%" for d in st.session_state["ride_data"]["gradient"]] 