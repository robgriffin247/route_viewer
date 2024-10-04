import streamlit as st
import duckdb
import os
import plotly.graph_objects as go

from dotenv import load_dotenv
load_dotenv()
load_dotenv('variables.env')

with duckdb.connect(os.getenv("DB")) as con:
    worlds = con.sql(f"""SELECT WORLD FROM INTERMEDIATE.OBT_FIT""").to_df()
    world = st.selectbox("World", worlds.world.unique(), index=len(list(worlds.world.unique()))-1)

    routes = con.sql(f"""SELECT ROUTE FROM INTERMEDIATE.OBT_FIT WHERE WORLD='{world}'""").to_df()
    route = st.selectbox("Route", routes.route.unique())

with duckdb.connect(os.getenv("DB")) as con:
    fit_data = con.sql(f"""SELECT * FROM INTERMEDIATE.OBT_FIT WHERE WORLD='{world}' AND ROUTE='{route}'""").to_df()
            
    route_profile = go.Figure()

    route_profile.add_trace(go.Scatter(x=fit_data["distance"], y=fit_data["altitude"], mode="lines", 
                                    #customdata=dt[["distance_fmt", "altitude_fmt"]],
                                    #hovertemplate="<b>Distance: %{customdata[0]}km</b><br>" + 
                                    #    "<b>Altitude: %{customdata[1]}m</b><br>" + 
                                    #    "<extra></extra>"
    ))

    route_profile.update_layout(xaxis_title="Distance (km)", yaxis_title="Altitude (m)")

    st.plotly_chart(route_profile)