import streamlit as st
import duckdb

with duckdb.connect("data/data.duckdb") as con:
        


    data = con.sql(f"SELECT world, route, fit, basic, complete FROM CORE.dim_routes WHERE priority=1 ORDER BY world, route").to_df()

    st.write("""
             I have checked through data on ZwiftPower events to pick out routes to prioritise &mdash; 
             these are among some of the most popular racing routes on Zwift so are most applicable to the target audience of this app!
             """)

    st.dataframe(data,
                 hide_index=True,
                 height=int(35.2*(data.shape[0]+1)),
                 use_container_width=True,
                 column_config={
                     "world":st.column_config.TextColumn("World"),
                     "route":st.column_config.TextColumn("Route"),
                     "fit":st.column_config.CheckboxColumn(".fit file"),
                     "basic":st.column_config.CheckboxColumn("Basic notes"),
                     "complete":st.column_config.CheckboxColumn("Full notes"),
                 })

