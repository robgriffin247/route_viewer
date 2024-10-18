
import streamlit as st 
import duckdb
import pandas as pd

def get_notes():
    with duckdb.connect("data/data.duckdb") as con:
        notes = con.sql(f"""
        SELECT segment, type, start_point, end_point, note,
                        CASE WHEN type IN ('sprint', 'climb', 'finish', 'lap_banner') THEN true ELSE false END AS highlight
        FROM CORE.dim_notes
        WHERE world='{st.session_state['world']}' AND route='{st.session_state['route']}'
        ORDER BY start_point
        """).to_df()

    x = """
    if st.session_state["can_lap"]:
        lead_length = notes.loc[notes["type"]=="lead", "end_km"][0]
        st.session_state["lap_length"] = [i for i in notes.loc[notes["type"]=="lap_banner", "end_km"]][0] - (lead_length)

        lap_data = notes.loc[notes["start_km"]>lead_length]
        for lap in range(st.session_state["laps"]-1):
            lap_data.loc[:, "start_km"] += st.session_state["lap_length"]
            lap_data.loc[:, "end_km"] += st.session_state["lap_length"]
            notes = pd.concat([notes, lap_data])
    """

    notes.loc[:, "start_point"] = pd.to_numeric(notes["start_point"])/st.session_state['convert_scale']
    notes.loc[:, "end_point"] = notes["end_point"]/st.session_state['convert_scale']
    notes.loc[:, "note"] = [str(i) for i in notes["note"]]

    #if st.session_state["basic"]:
    st.session_state["notes"] = notes
    #else:
    #    st.session_state["notes"] = notes.loc[notes["type"].isin(["sprint", "lead", "climb", "finish", "lap_banner"])]
        

    st.session_state["notes_data_editor"] = st.data_editor(st.session_state["notes"][["segment", "type", "highlight", "start_point", "end_point", "note"]],
                   hide_index=True, 
                   height=int(35.2*(st.session_state["notes"].shape[0]+1)),
                   use_container_width=True,
                   column_config={
                       "type":None,
                       "highlight":st.column_config.CheckboxColumn("🚨"),
                       "segment":st.column_config.TextColumn("Segment", width="medium"),
                       "start_point":st.column_config.NumberColumn("From", format=f"%.1f {st.session_state['d_unit']}", width="small"),
                       "end_point":st.column_config.NumberColumn("To", format=f"%.1f {st.session_state['d_unit']}", width="small"),
                       "note":st.column_config.TextColumn("Note", width="large")
                   }
                )
    
