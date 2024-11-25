import duckdb
import streamlit as st
import pandas as pd
import inspect

data_config = st.secrets['data_config']

# - Table of all gpx data for needed for plotting routes
# - Limited to lead in and first full lap
def int_rides():
    print(f'Running {inspect.stack()[0][3]}...')

    with duckdb.connect(f'{data_config["data_directory"]}/{data_config["test_db"]}') as con:
        df = con.sql(f"""
                        with rides as (
                            select world, route, distance, altitude
                        from {data_config["schema_stg"]}.stg_rides
                        ),

                        routes as (
                            select * from {data_config["schema_int"]}.int_routes
                        ),

                        joint as (
                            select rides.*, 
                                case when rides.distance < routes.lap_start then 0      
                                    when rides.distance <= routes.lap_finish then 1 
                                    else null end as lap
                            from rides left join routes on rides.world=routes.world and rides.route=routes.route
                            where rides.distance <= routes.lap_finish
                        ), 

                        add_gradient as (
                            select *,
                                case when row_number() over (partition by route, world order by distance) = 1 then 0 else (altitude - lag(altitude) over ()) / (distance - lag(distance) over ()) * 100 end as gradient
                            from joint 
                        ),

                        smooth_gradient as (
                            select * exclude(gradient),
                                mean(gradient) over (partition by route, world order by distance rows between 0 preceding and 2 following) as gradient
                            from add_gradient
                        )

                        select * from smooth_gradient
                    """).to_df()
    
        con.sql(f'create or replace table {data_config["schema_int"]}.{inspect.stack()[0][3]} as select * from df')

    return df
