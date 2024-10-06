import streamlit as st
import duckdb
import plotly.graph_objects as go
import pandas as pd

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
    fit_data = con.sql(f"""WITH route AS (
                            SELECT ROW_NUMBER() OVER () AS row, *, 
                            FROM INTERMEDIATE.OBT_FIT 
                            WHERE WORLD='{world}' AND ROUTE='{route}'
                        ),
                        
                       added_changes AS (
                            SELECT *,
                                    CASE WHEN LAG(distance) OVER () IS NOT NULL THEN distance - LAG(distance) OVER () ELSE 0 END AS distance_change,
                                    CASE WHEN LAG(altitude) OVER () IS NOT NULL THEN altitude - LAG(altitude) OVER () ELSE 0 END AS altitude_change
                            FROM route
                        ),

                        added_rollsums AS (
                            SELECT *,
                                sum(distance_change) OVER (ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING) AS distance_change_rollsum,
                                sum(altitude_change) OVER (ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING) AS altitude_change_rollsum
                            FROM added_changes
                        ),

                        added_rolling_gradient AS (
                            SELECT *, altitude_change_rollsum/distance_change_rollsum*100 AS grade
                            FROM added_rollsums
                        ),

                        scaled_units AS(
                            SELECT 
                                world,
                                route,
                                distance/1000 * {distance_scale} AS distance,
                                altitude * {altitude_scale} AS altitude,
                                CONCAT(ROUND(distance/1000 * {distance_scale}, 2), ' ', '{distance_unit}')  AS distance_fmt,
                                CONCAT(ROUND(altitude * {altitude_scale}, 2), ' ', '{altitude_unit}')  AS altitude_fmt,
                                grade,
                                CONCAT(ROUND(grade,1), '%') AS grade_fmt
                            FROM added_rolling_gradient
                        )

                        SELECT * FROM scaled_units    
                       
                       """).to_df()

    notes_data = con.sql(f"""SELECT 
                            true AS highlight,
                            name AS segment, 
                            round(start * {distance_scale}, 1) AS start, 
                            round("end" * {distance_scale}, 1) AS "end", 
                            note
                            FROM INTERMEDIATE.INT_ANNOTATIONS 
                            WHERE WORLD='{world}' AND ROUTE='{route}'""").to_df()

# Frontend:        

# User input to set the number of laps to generate
r2_1, r2_2, r2_3 = st.columns([5,5,6], vertical_alignment="bottom")
r2_1.number_input("Laps", min_value=1, max_value=1, value=1, step=1)
add_custom = r2_2.toggle("Custom Notes", value=False)

if add_custom:
    custom_notes = st.data_editor(pd.DataFrame({"highlight":[bool()], "segment":[None], "start":[None], "end":[None], "note":[None]}),
                                num_rows="dynamic",
                                column_config={
                                    "highlight":st.column_config.CheckboxColumn("Highlight", default=True),
                                    "segment":st.column_config.TextColumn("Segment"),
                                    "start":st.column_config.NumberColumn("From", format="%.1f"),
                                    "end":st.column_config.NumberColumn("To", format="%.1f"),
                                    "note":st.column_config.TextColumn("Notes", width="large"
                                    )
                                })
    
    notes_data = pd.concat([custom_notes, notes_data])
    
    #r3_1, r3_2, r3_3, r3_4, r3_5 = st.columns([4,2,2,6,2])
    #r3_1.text_input("Segment", value="")
    #r3_2.number_input("Start", min_value=0.0, format="%.1f")
    #r3_3.number_input("End", min_value=0.0, format="%.1f")
    #r3_4.text_input("Note", value="")
    #r3_5.button("add")

    race_notes = st.data_editor(notes_data,
                                column_config={
                                    "highlight":st.column_config.CheckboxColumn("Highlight", default=True),
                                    "segment":st.column_config.TextColumn("Segment"),
                                    "start":st.column_config.NumberColumn("From", format="%.1f"),
                                    "end":st.column_config.NumberColumn("To", format="%.1f"),
                                    "note":st.column_config.TextColumn("Notes", width="large"
                                    )                                    
                                })

else:
    race_notes = st.data_editor(notes_data,
                                column_config={
                                    "highlight":st.column_config.CheckboxColumn("Highlight", default=True),
                                    "segment":st.column_config.TextColumn("Segment"),
                                    "start":st.column_config.NumberColumn("From", format="%.1f"),
                                    "end":st.column_config.NumberColumn("To", format="%.1f"),
                                    "note":st.column_config.TextColumn("Notes", width="large"
                                    )                                    
                                })
# Add grade to notes table
# Add profile to notes table (if max grade >=5% or average >=2%)
# Add loop variable to routes data - make laps control action max 1 if not loop
# Trim fit data to one lap per route

profile_plot = go.Figure()

profile_plot.add_trace(go.Scatter(
    x=fit_data["distance"], 
    y=fit_data["altitude"], 
    mode="lines",
    fill="tozeroy",
    # fillcolor="red", # create a gradient connected to grade variable
    customdata=fit_data[["distance_fmt", "altitude_fmt", "grade_fmt"]],
    hovertemplate="<b>Distance: %{customdata[0]}</b><br>" + "<b>Altitude: %{customdata[1]}</b><br>" + "<b>Grade: %{customdata[2]}</b><br>" + "<extra></extra>"
    ))

for s in race_notes.iterrows():
    if s[1].highlight:
        profile_plot.add_vrect(x0=s[1].start, x1=s[1].end, line_width=0, fillcolor="red", opacity=0.2)
        # Cont from here - add fill colors and remove borders

profile_plot.update_layout(
    xaxis_title=f"Distance ({distance_unit})", 
    yaxis_title=f"Altitude ({altitude_unit})")


st_profile_plot = st.plotly_chart(profile_plot)

