import streamlit as st
import duckdb
import plotly.graph_objects as go


# User input to select route and set units
col1, col2, col3 = st.columns(3)

metric = st.toggle("Metric", value=True)

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
    world = col1.selectbox("World", worlds.world.unique(), index=len(list(worlds.world.unique()))-1)

    # User input to select route (as a child of world)
    routes = con.sql(f"""SELECT ROUTE FROM INTERMEDIATE.OBT_FIT WHERE WORLD='{world}'""").to_df()
    route = col2.selectbox("Route", routes.route.unique())

    # User input to set the number of laps to generate
    # col3.number_input("Laps", min_value=1, max_value=1, value=1, step=1)

    # Get the route data
    fit_data = con.sql(f"""SELECT 
                            distance/1000 * {distance_scale} AS distance,
                            altitude * {altitude_scale} AS altitude,
                            CONCAT(ROUND(distance/1000 * {distance_scale}, 2), '{distance_unit}')  AS distance_fmt,
                            CONCAT(ROUND(altitude * {altitude_scale}, 2), '{altitude_unit}')  AS altitude_fmt,
                            CASE WHEN LAG(altitude) OVER () IS NOT NULL THEN altitude - LAG(altitude) OVER () ELSE 0 END AS altitude_change
                       FROM INTERMEDIATE.OBT_FIT 
                       WHERE WORLD='{world}' AND ROUTE='{route}'""").to_df()
    
    st.write(fit_data)
#x_range = st.slider("", value=(0.0, fit_data["distance"].max()), min_value=0.0, max_value=fit_data["distance"].max(), step=0.01)
#vis_data = fit_data[(fit_data["distance"]>=x_range[0]) & (fit_data["distance"]<=x_range[1])]


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



#distance = vis_data.iloc[-1]["distance"] - vis_data.iloc[0]["distance"]
#elevation_diff = vis_data.iloc[-1]["altitude"] - vis_data.iloc[0]["altitude"]
#elevation_gain = sum(vis_data["step_elevation_gain"])
#if metric:
#    grade = elevation_diff / distance / 10
#else:
#    grade = (elevation_diff*0.0189393939) / distance

#col4, col5, col6 = st.columns(3)

#col4.write(f"Length: {round(distance,2)} {distance_unit}")
#col5.write(f"Total Climb: {int(elevation_gain)} {altitude_unit}")
#col6.write(f"Average Grade: {round(grade,2)}%")
