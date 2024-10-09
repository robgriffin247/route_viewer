import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

st.html("html/google_analytics.html")

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
            h2 {
                padding: 0 auto 2em auto;
                margin: 0 auto 1.2em auto;
                border-bottom: 1px solid #304d4b;
            }
            .stDataFrame {
                width: 100% !important;
            }
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

#in_platform, in_world = st.columns(2)
in_world, in_route, in_metric = st.columns([3,5,2], vertical_alignment="bottom")
#in_route, in_metric = st.columns([55,9], vertical_alignment="bottom")
profile_plot_container = st.container()
route_notes_container = st.container()
st.html("<p class='footnote'>Produced by Rob Griffin. It's early days - this project is very much in its infancy and requires more data. I'm running a bot around various routes to generate more route data, while watching races to develop notes. It takes time, but it'll be worth   the wait!</p>")
# Populate dropdown menus for route selection and define logic for metric toggle ===================================
# Dynamic lists of valid platforms/worlds/routes; produces dropdown menus (selectbox)
with duckdb.connect("data/data.duckdb") as con:

    platform="Zwift"

    world = in_world.selectbox(
        label="**World**", 
        index=0, 
        options=con.sql(f"""SELECT DISTINCT(WORLD) FROM CORE.DIM_FIT WHERE PLATFORM='{platform}' ORDER BY WORLD""").to_df(), 
    )

    route = in_route.selectbox(
        label="**Route**", 
        index=0, 
        options=con.sql(f"""SELECT DISTINCT(ROUTE) FROM CORE.DIM_FIT WHERE PLATFORM='{platform}' AND WORLD='{world}' ORDER BY ROUTE""").to_df(), 
    )

in_metric.toggle("Metric", value=st.session_state["metric"], on_change=handle_metric, key="metric")

# Produce route data for plotting ===============================================================================
with duckdb.connect("data/data.duckdb") as con:

    route_data = con.sql(f"""
                            WITH SOURCE AS (
                                SELECT 
                                    distance, 
                                    altitude
                                FROM CORE.DIM_FIT
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
                                    altitude_delta,
                                    grade,                                  
                                    altitude*{st.session_state["altitude_scale"]} AS altitude,
                                    distance*{st.session_state["distance_scale"]} AS distance
                                FROM GRADE
                            ),

                            FORMAT AS (
                                SELECT *,
                                    CONCAT(ROUND(altitude, 1), ' {st.session_state["altitude_unit"]}') AS altitude_fmt,
                                    CONCAT(ROUND(distance, 2), ' {st.session_state["distance_unit"]}') AS distance_fmt,
                                    CONCAT(ROUND(grade, 1), '%') AS grade_fmt
                                FROM SCALE
                            )

                            SELECT *, FROM FORMAT
                            """).to_df()

# Notes Table =====================================================================================================
with duckdb.connect("data/data.duckdb") as con:
    base_notes = con.sql(f"""SELECT 
                                CASE WHEN type IS NULL THEN false ELSE true END AS highlight,
                                name AS segment, 
                                type,
                                start * {st.session_state['distance_scale']} AS start, 
                                "end" * {st.session_state['distance_scale']} AS "end",
                                note
                                FROM CORE.DIM_ANNOTATIONS 
                                WHERE WORLD='{world}' AND ROUTE='{route}'""").to_df()

if len(base_notes) != 0:
    route_notes_container.dataframe(base_notes[["segment", "start", "end", "note"]], 
                                    hide_index=True, 
                                    column_config={
                                        "segment":st.column_config.TextColumn("Segment", width="medium"),
                                        "start":st.column_config.NumberColumn("From", format="%.2f", width="small"),
                                        "end":st.column_config.NumberColumn("To", format="%.2f", width="small"),
                                        "note":st.column_config.TextColumn("Notes", width="large")
                                    })


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
        if s[1].type=="lead":
            profile_plot.add_vrect(x0=s[1].start, x1=s[1].end, line_width=0, fillcolor="orange", opacity=0.3)
        
        elif s[1].type=="sprint":
            profile_plot.add_vrect(x0=s[1].start, x1=s[1].end, line_width=0, fillcolor="green", opacity=0.3)
            
        elif s[1].type=="climb":
            profile_plot.add_vrect(x0=s[1].start, x1=s[1].end, line_width=0, fillcolor="red", opacity=0.3)
        
        elif s[1].type=="highlight":
            profile_plot.add_vrect(x0=s[1].start, x1=s[1].end, line_width=0, fillcolor="yellow", opacity=0.3)
            
        elif s[1].type=="finish":
            profile_plot.add_vline(x=s[1].end, line_color="red", opacity=0.5)

        else:
#            profile_plot.add_vrect(x0=s[1].start, x1=s[1].end, line_width=0, fillcolor="blue", opacity=0.2)
            pass

profile_plot_container.plotly_chart(profile_plot)
