import streamlit as st 
import duckdb

with duckdb.connect("data/data.duckdb") as con:

    to_do = con.sql("""
            WITH ROUTES AS (
                SELECT route_id, world, route, total_length FROM INTERMEDIATE.int_routes WHERE ride
            ),
            ROUTES_RIDDEN AS (
                SELECT DISTINCT(route_id) AS route_id
                FROM INTERMEDIATE.int_rides
            )
            SELECT world, route, total_length FROM ROUTES WHERE route_id NOT IN (SELECT route_id FROM ROUTES_RIDDEN) ORDER BY total_length
            """)

    st.dataframe(to_do, 
                 hide_index=True,
                 use_container_width=True,
                 column_config={
                    "world":st.column_config.TextColumn("World"),
                    "route":st.column_config.TextColumn("Route"),
                    "total_length":st.column_config.NumberColumn("Length (km)", format='%.1f'),
                 })
    
    if False:
        st.html("<hr/><br/>")
        st.write("Ridden a race on one of these routes starting from the pens and covering the entire route? Download the .gpx file from Strava and upload it here!")
        upload_area, send_button = st.columns([8,3])
        # Control type
        upload_area.file_uploader("Upload .gpx file", label_visibility="hidden")
        # inactive if no file uploaded
        send_button.button("Send")
        # Send file to me
        # Generate pop up thank you message