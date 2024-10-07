import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px


if "metric" not in st.session_state:
    st.session_state["altitude_scale"] = 1
    st.session_state["altitude_unit"] = "m"
    st.session_state["distance_scale"] = 1
    st.session_state["distance_unit"] = "km"
    st.session_state["metric"] = True

# Acts on toggle of in_metric - allowing user to control if metric or imperial, causes downstream calculations and formatting    
def handle_metric():
    if st.session_state["metric"]:
        st.session_state["altitude_scale"] = 1
        st.session_state["altitude_unit"] = "m"
        st.session_state["distance_scale"] = 1
        st.session_state["distance_unit"] = "km"
    else:
        st.session_state["altitude_scale"] = 1/0.3048
        st.session_state["altitude_unit"] = "ft"
        st.session_state["distance_scale"] = 0.621371192
        st.session_state["distance_unit"] = "miles"

# Generate Layout ==================================================================================================
st.html("""
        <style> 
            .footnote {
                color: #304d4b;
                font-style:italic;
                border-top: 1px solid #304d4b;
                padding: 1em 0 0 0;
                margin: 10em auto
            }
        </style>
        """)

st.header("RouteViewer")

in_platform, in_world = st.columns(2)
in_route, in_metric = st.columns([55,9], vertical_alignment="bottom")
profile_plot_container = st.container()
route_notes_container = st.container()
st.html("<p class='footnote'>Produced by Rob Griffin</p>")

# Populate dropdown menus for route selection and define logic for metric toggle ===================================
# Dynamic lists of valid platforms/worlds/routes; produces dropdown menus (selectbox)
with duckdb.connect("data/data.duckdb") as con:
    platform = in_platform.selectbox(
        label="**Platform**", 
        index=0, 
        options=con.sql(f"""SELECT DISTINCT(PLATFORM) FROM INTERMEDIATE.OBT_FIT ORDER BY PLATFORM""").to_df(), 
    )

    world = in_world.selectbox(
        label="**World**", 
        index=3, 
        options=con.sql(f"""SELECT DISTINCT(WORLD) FROM INTERMEDIATE.OBT_FIT WHERE PLATFORM='{platform}' ORDER BY WORLD""").to_df(), 
    )

    route = in_route.selectbox(
        label="**Route**", 
        index=0, 
        options=con.sql(f"""SELECT DISTINCT(ROUTE) FROM INTERMEDIATE.OBT_FIT WHERE PLATFORM='{platform}' AND WORLD='{world}' ORDER BY ROUTE""").to_df(), 
    )

in_metric.toggle("Metric", value=st.session_state["metric"], on_change=handle_metric, key="metric")

# Produce route data for plotting ===============================================================================
with duckdb.connect("data/data.duckdb") as con:

    route_data = con.sql(f"""
                            WITH SOURCE AS (
                                SELECT 
                                    distance, 
                                    altitude
                                FROM INTERMEDIATE.OBT_FIT
                                WHERE platform='{platform}'
                                    AND world='{world}'
                                    AND route='{route}'
                            ),

                            DELTA AS (
                                SELECT 
                                    distance/1000 AS distance,
                                    altitude,
                                    CASE WHEN LAG(altitude) OVER () IS NOT NULL THEN altitude - LAG(altitude) OVER () ELSE 0 END AS altitude_delta,
                                    CASE WHEN LAG(distance) OVER () IS NOT NULL THEN distance - LAG(distance) OVER () ELSE 0 END AS distance_delta
                                FROM SOURCE
                            ),

                            GRADE AS (
                                SELECT *,
                                    altitude_delta/distance_delta*100 AS grade
                                FROM DELTA
                            ),

                            SCALE AS (
                                SELECT
                                    grade,                                  
                                    altitude*{st.session_state["altitude_scale"]} AS altitude,
                                    distance*{st.session_state["distance_scale"]} AS distance
                                FROM GRADE
                            ),

                            FORMAT AS (
                                SELECT *,
                                    CONCAT(ROUND(altitude, 1), '{st.session_state["altitude_unit"]}') AS altitude_fmt,
                                    CONCAT(ROUND(distance, 1), '{st.session_state["distance_unit"]}') AS distance_fmt,
                                    CONCAT(ROUND(grade, 1), '%') AS grade_fmt
                                FROM SCALE
                            )

                            SELECT *, FROM FORMAT
                            """).to_df()

# Notes Table =====================================================================================================
with duckdb.connect("data/data.duckdb") as con:
    base_notes = con.sql(f"""SELECT 
                                CASE WHEN type IN ('lead-in', 'finish') THEN false ELSE true END AS highlight,
                                name AS segment, 
                                type,
                                start * {st.session_state['distance_scale']} AS start, 
                                "end" * {st.session_state['distance_scale']} AS "end", 
                                format('{{:0.2f}}', start * {st.session_state['distance_scale']}) AS from, 
                                format('{{:0.2f}}', "end" * {st.session_state['distance_scale']}) AS to, 
                                note
                                FROM INTERMEDIATE.INT_ANNOTATIONS 
                                WHERE WORLD='{world}' AND ROUTE='{route}'""").to_df()

route_notes_container.dataframe(base_notes[["segment", "from", "to", "note"]], hide_index=True)


# Main Plot =====================================================================================================
profile_plot = px.line(route_data, 
                       x="distance", 
                       y="altitude",
                       labels={"distance":f"Distance ({st.session_state['distance_unit']})",
                               "altitude":f"Altitude ({st.session_state['altitude_unit']})"})

profile_plot.update_traces(mode="lines",
                           customdata=route_data[["distance_fmt", "altitude_fmt", "grade_fmt"]],
                           hovertemplate="<b>Distance: %{customdata[0]}</b><br>" + "<b>Altitude: %{customdata[1]}</b><br>" + "<b>Grade: %{customdata[2]}</b><br>" + "<extra></extra>"
                           )

for s in base_notes.iterrows():
    if s[1].highlight:
        if s[1].type=="lead-in":
            profile_plot.add_vrect(x0=s[1].start, x1=s[1].end, line_width=0, fillcolor="orange", opacity=0.2)
        
        elif s[1].type=="sprint":
            profile_plot.add_vrect(x0=s[1].start, x1=s[1].end, line_width=0, fillcolor="green", opacity=0.2)
            
        elif s[1].type=="climb":
            profile_plot.add_vrect(x0=s[1].start, x1=s[1].end, line_width=0, fillcolor="red", opacity=0.2)
            
        elif s[1].type=="finish":
            profile_plot.add_vline(x=s[1].end, line_color="red", opacity=0.5)

        else:
            profile_plot.add_vrect(x0=s[1].start, x1=s[1].end, line_width=0, fillcolor="blue", opacity=0.2)

profile_plot_container.plotly_chart(profile_plot)
