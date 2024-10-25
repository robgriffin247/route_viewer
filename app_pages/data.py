import streamlit as st 
import duckdb
from pipeline.read_raw import read_gpx
import os 

with duckdb.connect(f'{os.getenv("data_dir")}/{os.getenv("database")}') as con:

    to_do = con.sql("""
            WITH ROUTES AS (
                SELECT world, route, lead + lap AS total 
                FROM CORE.dim_routes
            ),
            ROUTES_RIDDEN AS (
                SELECT DISTINCT(world), route
                FROM CORE.dim_rides
            )
            SELECT world, route FROM ROUTES WHERE CONCAT(world, '_', route) NOT IN (SELECT CONCAT(world, '_', route) FROM ROUTES_RIDDEN) ORDER BY world, route
            """)
    
    done = con.sql("""
                SELECT COUNT(DISTINCT(world, route)) AS n
                FROM CORE.dim_rides
            """).to_df()

    st.write(f"GPX files for {done.loc[0, 'n']} routes collected, {to_do.shape[0]} to go:")


    st.dataframe(to_do, 
                 hide_index=True,
                 use_container_width=True,
                 column_config={
                    "world":st.column_config.TextColumn("World"),
                    "route":st.column_config.TextColumn("Route")
                 })
    

    if False:
        st.html("<hr/><br/>")
        st.write("Ridden a race on one of these routes starting from the pens and covering the entire route? Download the .gpx file from Strava and upload it here!")
        # Control type
        # Send file to me
        # Generate pop up thank you message
