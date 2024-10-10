import streamlit as st
import duckdb

def get_fit(world="", route="", metric=True):

    if metric:
        altitude_scale = 1
        altitude_unit = "m"
        distance_scale = 0.001
        distance_unit = "km"
    else:
        altitude_scale = 3.2808399
        altitude_unit = "ft"
        distance_scale = 0.6213712/1000
        distance_unit = "miles"

    with duckdb.connect("data/data.duckdb") as con:
        query = f"WITH SOURCE AS (SELECT * FROM CORE.DIM_FIT"
        if world!="" or route!="":
            query += " WHERE  "
            if world!="" and route!="":
                query += f"WORLD='{world}' AND ROUTE='{route}'"
            elif world!="":
                query += f"WORLD='{world}'"
            else:
                query += f"ROUTE='{route}'"
        else:
            pass            
        
        query += f"""),

        DELTAS AS (
            SELECT
                world, route, altitude, distance,
                CASE WHEN LAG(altitude) OVER() IS NULL THEN 0 ELSE altitude - LAG(altitude) OVER() END AS delta_altitude,
                CASE WHEN LAG(distance) OVER() IS NULL THEN 0 ELSE distance - LAG(distance) OVER() END AS delta_distance
            FROM SOURCE
        ),

        GRADIENTS AS (
            SELECT
                world, route, altitude, distance, delta_altitude,
                CASE WHEN delta_distance=0 THEN 0 ELSE delta_altitude/delta_distance END AS gradient
            FROM DELTAS
        ),

        CONVERSIONS AS (
            SELECT
                world, route, 
                delta_altitude * {altitude_scale} AS delta_altitude,
                altitude * {altitude_scale} AS altitude, 
                distance * {distance_scale} AS distance, 
                gradient
            FROM GRADIENTS
        ),

        FORMATS AS (
            SELECT *,
                CONCAT(ROUND(altitude, 1), ' {altitude_unit}') AS formatted_altitude,
                CONCAT(ROUND(distance, 2), ' {distance_unit}') AS formatted_distance,
                CONCAT(ROUND(gradient, 1), '%') as formatted_gradient
            FROM CONVERSIONS
        )
        
        SELECT * FROM FORMATS

        """

        data = con.sql(query).to_df()
        
        return data

def get_notes(world="", route="", metric=True):
    
    if metric:
        distance_scale = 1
    else:
        distance_scale = 0.6213712

    with duckdb.connect("data/data.duckdb") as con:
        data = con.sql(f"""
            SELECT 
                name AS Segment,
                start*{distance_scale} AS From, 
                "end"*{distance_scale} AS To,
                note AS Notes
            FROM CORE.DIM_ANNOTATIONS WHERE WORLD = '{world}' AND ROUTE = '{route}'
        """).to_df()

    return data 