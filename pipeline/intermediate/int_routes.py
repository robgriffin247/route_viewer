import duckdb
import streamlit as st
import pandas as pd
import inspect

data_config = st.secrets['data_config']

# - Create a table with all routes
# - Use data from routes where possible
def int_routes(route=False):
    print(f'Running {inspect.stack()[0][3]}...')

    with duckdb.connect(f'{data_config["data_directory"]}/{data_config["database_name"]}') as con:
        df = con.sql(f"""
                        with zi_routes as (
                            select world, route,
                                cast(str_split(lead, 'km')[1] as float) * 1000 as lead,
                                (cast(str_split(total, 'km')[1] as float) * 1000) + (cast(str_split(lead, 'km')[1] as float) * 1000) as total
                            from {data_config["schema_stg"]}.stg_zi_routes
                            where lower(restriction) not like '%run only%' or restriction is null
                        ),

                        routes as (
                            select *
                            from {data_config["schema_stg"]}.stg_routes
                        ),

                        joint as (
                            select zi.world, zi.route, r.circuit, r.first_lap_whole,
                                case when r.full_route_start is not null then FALSE else TRUE end as zi_data,
                                case when r.full_route_start is not null then r.full_route_start else zi.lead end as lap_start,
                                case when r.full_route_finish is not null then r.full_route_finish else zi.total end as lap_finish
                            from zi_routes as zi left join routes as r on zi.world=r.world and zi.route=r.route
                        ),

                        add_length as (
                            select *, lap_finish - lap_start as route_length from joint
                        )

                        select * from add_length order by world, route, lap_finish
                    """).to_df()
    
        con.sql(f'create or replace table {data_config["schema_int"]}.{inspect.stack()[0][3]} as select * from df')

    if route:
        df = df.loc[df.route==route]
    return df
