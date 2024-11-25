import duckdb
import streamlit as st
import pandas as pd
import inspect

data_config = st.secrets['data_config']

# - Gives combined data of notes for all routes
def int_notes():
    print(f'Running {inspect.stack()[0][3]}...')

    with duckdb.connect(f'{data_config["data_directory"]}/{data_config["test_db"]}') as con:
        df = con.sql(f"""
                        with sectors as (
                            select * from {data_config["schema_stg"]}.stg_sectors
                        ),

                        notes as (
                            select * from {data_config["schema_stg"]}.stg_notes
                        ),

                        waypoints as (
                            select * from {data_config["schema_stg"]}.stg_waypoints
                        ),

                        adjusted_notes as (
                            select n.* exclude(note_start, note_end),
                                n.note_start - s.sector_start as note_start, 
                                n.note_end - s.sector_start as note_end 
                            from notes as n left join sectors as s on n.sector_id=s.sector_id)
                        
                        select w.world, w.route, 
                            an.note_title,
                            w.sector_start + an.note_start as note_start,
                            w.sector_start + an.note_end as note_end,
                            an.note_type,
                            case when an.note_type is not null then TRUE else FALSE end as highlight,
                            an.note
                        from waypoints as w left join adjusted_notes as an on w.sector_id=an.sector_id
                    """).to_df()
    
        con.sql(f'create or replace table {data_config["schema_int"]}.{inspect.stack()[0][3]} as select * from df')

    return df 
