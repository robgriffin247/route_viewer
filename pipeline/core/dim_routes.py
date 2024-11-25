import duckdb
import streamlit as st
import inspect
import polars as pl

data_config = st.secrets['data_config']

def dim_routes():
    print(f'Running {inspect.stack()[0][3]}...')

    with duckdb.connect(f'{data_config["data_directory"]}/{data_config["database_name"]}') as con:
        
        df = con.sql(f"""
                        with rides as (
                            select world, route, TRUE as gpx_parsed 
                        from {data_config["schema_int"]}.int_rides
                        group by world, route
                        ),
                        routes as (
                            select * from {data_config["schema_int"]}.int_routes
                        ),
                        joint as (
                            select routes.* from routes left join rides on routes.world=rides.world and routes.route=rides.route where (rides.gpx_parsed)
                        )
                        select * from joint

                     """).to_df()

        con.sql(f'create or replace table {data_config["schema_prd"]}.{inspect.stack()[0][3]} as select * from df')
 