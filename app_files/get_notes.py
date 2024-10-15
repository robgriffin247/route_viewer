import streamlit as st 
import duckdb
import pandas as pd

def get_notes():
    with duckdb.connect("data/data.duckdb") as con:
        notes = con.sql(f"""
        SELECT segment, type, start_km, end_km, note,
                        CASE WHEN type IN ('sprint', 'climb', 'finish', 'lap_banner') THEN true ELSE false END AS highlight
        FROM CORE.dim_notes
        WHERE world='{st.session_state['world']}' AND route='{st.session_state['route']}'
        """).to_df()

   
    lead_length = float(notes[notes["type"]=="lead"]["end_km"])
    st.session_state["lap_length"] = float(notes[(notes["type"]=="finish") | (notes["type"]=="lap_banner")]["end_km"]) - (lead_length)#/st.session_state["convert_scale"])

    lap_data = notes[notes["start_km"]>lead_length]
    for lap in range(st.session_state["laps"]-1):
        lap_data["start_km"] += st.session_state["lap_length"]
        lap_data["end_km"] += st.session_state["lap_length"]
        notes = pd.concat([notes, lap_data])

    notes["start_point"] = (notes["start_km"]/st.session_state['convert_scale'])
    notes["end_point"] = (notes["end_km"]/st.session_state['convert_scale'])

    st.session_state["notes"] = notes

    st.session_state["notes_data_editor"] = st.data_editor(st.session_state["notes"][["segment", "type", "highlight", "start_point", "end_point", "note"]],
                   hide_index=True, 
                   height=int(35.2*(notes.shape[0]+1)),
                   use_container_width=False,
                   column_config={
                       "type":None,
                       "highlight":st.column_config.CheckboxColumn("🚨"),
                       "segment":st.column_config.TextColumn("Segment", width="medium"),
                       "start_point":st.column_config.NumberColumn("From", format=f"%.2f {st.session_state['d_unit']}", width="small"),
                       "end_point":st.column_config.NumberColumn("To", format=f"%.2f {st.session_state['d_unit']}", width="small"),
                       "note":st.column_config.TextColumn("Note", width="large")
                   },
                   disabled=["segment", "start_point", "end_point", "notes"])

