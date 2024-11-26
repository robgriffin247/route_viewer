import streamlit as st
import polars as pl

def user_input_settings():
    # This does a lot 
    # - setting units for later formatting if metric/imperial
    # - converting values between imperial and metric
    # - building data depending on the number of laps (complex due to false lead ins (e.g. Douce France))
    # Laps ---------------------------------------------------------------------------------------
    laps_input, metric_input, _ = st.columns([3,3,6], vertical_alignment="bottom")

    if st.session_state["routes_focal"]["circuit"].item():
        laps_input.number_input("Laps", key="laps", min_value=1, max_value=20, value=1)
    elif st.session_state["routes_focal"]["circuit"].item()==False:
        laps_input.number_input("Laps", key="laps", min_value=1, max_value=1, value=1, help="Route is not a circuit - cannot do more than one lap!")
    else:
        laps_input.number_input("Laps", key="laps", min_value=1, max_value=20, value=1, help="This route has not yet been annotated and lapping behaviour may be innacurate - bear this in mind!")
        
    lead_ride = st.session_state["rides_focal"].filter(pl.col("distance")<st.session_state["routes_focal"].select("lap_start").item())
    lead_notes = st.session_state["notes_focal"].filter(pl.col("note_start")<st.session_state["routes_focal"].select("lap_start").item())
    lap_ride = st.session_state["rides_focal"].filter(
        (pl.col("distance")>=st.session_state["routes_focal"].select("lap_start").item()) &
        (pl.col("distance")<=st.session_state["routes_focal"].select("lap_finish").item()))
    lap_notes = st.session_state["notes_focal"].filter(
        (pl.col("note_start")>=st.session_state["routes_focal"].select("lap_start").item()) &
        (pl.col("note_end")<=st.session_state["routes_focal"].select("lap_finish").item()))

    st.session_state["rides_focal"] = lead_ride
    st.session_state["notes_focal"] = lead_notes
    if (st.session_state["routes_focal"]["first_lap_whole"].item()) or (st.session_state["routes_focal"]["first_lap_whole"].item() is None):
        for lap in range(1, st.session_state["laps"]+1):
            if lap>1:
                lap_ride = lap_ride.with_columns(distance=(pl.col("distance")+st.session_state["routes_focal"].select("route_length").item()))
                lap_notes = lap_notes.with_columns(note_start=(pl.col("note_start")+int(st.session_state["routes_focal"].select("route_length").item())))
                lap_notes = lap_notes.with_columns(note_end=(pl.col("note_end")+int(st.session_state["routes_focal"].select("route_length").item())))
            st.session_state["rides_focal"] = pl.concat([st.session_state["rides_focal"], lap_ride])
            st.session_state["notes_focal"] = pl.concat([st.session_state["notes_focal"], lap_notes])
    else:
        for lap in range(2, st.session_state["laps"]+1):
            if lap>2:
                lap_ride = lap_ride.with_columns(distance=(pl.col("distance")+st.session_state["routes_focal"].select("route_length").item()))
                lap_notes = lap_notes.with_columns(note_start=(pl.col("note_start")+int(st.session_state["routes_focal"].select("route_length").item())))
                lap_notes = lap_notes.with_columns(note_end=(pl.col("note_end")+int(st.session_state["routes_focal"].select("route_length").item())))
            st.session_state["rides_focal"] = pl.concat([st.session_state["rides_focal"], lap_ride])
            st.session_state["notes_focal"] = pl.concat([st.session_state["notes_focal"], lap_notes])

    # Remove dup note_titles
    #st.session_state["notes_focal"] = st.session_state["notes_focal"].with_columns(note_title=pl.when(pl.col("note_title").shift(1)!=pl.col("note_title")).then(pl.col("note_title")).otherwise(-1))

    # Metric --------------------------------------------------------------------------------------
    metric_input.toggle("Metric", key="metric", value=True)

    # Units to be used for figures and tables
    if st.session_state["metric"]:
        st.session_state["dst_units"] = 'km'
        st.session_state["alt_units"] = 'm'
        st.session_state["rides_focal"] = st.session_state["rides_focal"].with_columns((pl.col("distance").mul(0.001)).alias("distance"))
        st.session_state["notes_focal"] = st.session_state["notes_focal"].with_columns((pl.col("note_start").mul(0.001)).alias("note_start"))
        st.session_state["notes_focal"] = st.session_state["notes_focal"].with_columns((pl.col("note_end").mul(0.001)).alias("note_end"))
    
    else:
        st.session_state["dst_units"] = 'mi'
        st.session_state["alt_units"] = 'ft'
        st.session_state["rides_focal"] = st.session_state["rides_focal"].with_columns((pl.col("distance").mul(0.000621371192)).alias("distance"))
        st.session_state["rides_focal"] = st.session_state["rides_focal"].with_columns((pl.col("altitude").mul(3.2808399)).alias("altitude"))
        st.session_state["notes_focal"] = st.session_state["notes_focal"].with_columns((pl.col("note_start").mul(0.000621371192)).alias("note_start"))
        st.session_state["notes_focal"] = st.session_state["notes_focal"].with_columns((pl.col("note_end").mul(0.000621371192)).alias("note_end"))
