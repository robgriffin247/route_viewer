import streamlit as st
import duckdb
import plotly.graph_objects as go


# User input to select route and set units
r1_1, r1_2, r1_3 = st.columns([5,8,3], vertical_alignment="bottom")

metric = r1_3.toggle("Metric", value=True)

if metric:
    distance_scale = 1
    altitude_scale = 1
    distance_unit = "km"
    altitude_unit = "m"
else:
    distance_scale = 0.62137
    altitude_scale = 3.28084
    distance_unit = "miles"
    altitude_unit = "ft"


with duckdb.connect("data/data.duckdb") as con:
    # User input to select world
    worlds = con.sql(f"""SELECT WORLD FROM INTERMEDIATE.OBT_FIT""").to_df()
    world = r1_1.selectbox("World", worlds.world.unique(), index=len(list(worlds.world.unique()))-1)

    # User input to select route (as a child of world)
    routes = con.sql(f"""SELECT ROUTE FROM INTERMEDIATE.OBT_FIT WHERE WORLD='{world}'""").to_df()
    route = r1_2.selectbox("Route", routes.route.unique())

    # Get the route data
    fit_data = con.sql(f"""SELECT 
                            distance/1000 * {distance_scale} AS distance,
                            altitude * {altitude_scale} AS altitude,
                            CONCAT(ROUND(distance/1000 * {distance_scale}, 2), '{distance_unit}')  AS distance_fmt,
                            CONCAT(ROUND(altitude * {altitude_scale}, 2), '{altitude_unit}')  AS altitude_fmt,
                            CASE WHEN LAG(altitude) OVER () IS NOT NULL THEN altitude - LAG(altitude) OVER () ELSE 0 END AS altitude_change
                       FROM INTERMEDIATE.OBT_FIT 
                       WHERE WORLD='{world}' AND ROUTE='{route}'""").to_df()

# Frontend:        
profile_plot = go.Figure()

profile_plot.add_trace(go.Scatter(
    x=fit_data["distance"], 
    y=fit_data["altitude"], 
    mode="lines",
    customdata=fit_data[["distance_fmt", "altitude_fmt"]],
    hovertemplate="<b>Distance: %{customdata[0]}</b><br>" + "<b>Altitude: %{customdata[1]}</b><br>" + "<extra></extra>"
    ))

profile_plot.update_layout(
    xaxis_title=f"Distance ({distance_unit})", 
    yaxis_title=f"Altitude ({altitude_unit})")


profile_plot = st.plotly_chart(profile_plot)

# User input to set the number of laps to generate
st.number_input("Laps", min_value=1, max_value=1, value=1, step=1)

