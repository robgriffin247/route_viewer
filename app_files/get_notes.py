import streamlit as st 
import duckdb
import pandas as pd
def get_notes():

    #with duckdb.connect("data/data.duckdb") as con:
    #    st.session_state["notes"] = con.sql(f"""SELECT 
    #                            world, 
    #                            route, 
    #                            segment, 
    #                            type,
    #                            CASE WHEN type IN ('sprint', 'climb') THEN true ELSE false END AS highlight,
    #                            start_km/{st.session_state['convert_scale']} AS start_point, 
    #                            end_km/{st.session_state['convert_scale']} AS end_point, notes 
    #                        FROM CORE.dim_notes 
    #                        WHERE world='{st.session_state['world']}' AND route='{st.session_state['route']}'""").to_df()

    with duckdb.connect("data/data.duckdb") as con:
        st.session_state["lead_length"] = con.sql(f"""
                                    SELECT end_km/{st.session_state['convert_scale']} AS x
                                    FROM CORE.dim_notes 
                                    WHERE world='{st.session_state['world']}' 
                                        AND route='{st.session_state['route']}' 
                                        AND type=='lead'""").to_df()["x"][0]
        
        st.session_state["lead_notes"] = con.sql(f"""SELECT 
                                world, 
                                route, 
                                segment, 
                                type,
                                CASE WHEN type IN ('sprint', 'climb') THEN true ELSE false END AS highlight,
                                start_km/{st.session_state['convert_scale']} AS start_point, 
                                end_km/{st.session_state['convert_scale']} AS end_point, 
                                notes,
                                0 AS lap
                            FROM CORE.dim_notes 
                            WHERE world='{st.session_state['world']}' AND route='{st.session_state['route']}' AND end_point<={st.session_state["lead_length"] }""").to_df()
        
        lead_notes = st.session_state["lead_notes"]

        st.session_state["lap_notes"] = con.sql(f"""SELECT 
                                world, 
                                route, 
                                segment, 
                                type,
                                CASE WHEN type IN ('sprint', 'climb') THEN true ELSE false END AS highlight,
                                start_km/{st.session_state['convert_scale']} AS start_point, 
                                end_km/{st.session_state['convert_scale']} AS end_point, 
                                notes,
                                1 AS lap
                            FROM CORE.dim_notes 
                            WHERE world='{st.session_state['world']}' AND route='{st.session_state['route']}' 
                                AND {st.session_state["lead_length"] }<=start_point""").to_df()
        
        
    st.session_state["notes"] = pd.concat([st.session_state["lead_notes"], st.session_state["lap_notes"]])
    st.session_state["lap_length"] = float(st.session_state["lap_notes"].loc[st.session_state["lap_notes"]["type"]=="finish", "end_point"]) - st.session_state["lead_length"] 


    temp = st.session_state["lap_notes"]
    for lap in range(st.session_state["laps"]):
        temp["start_point"] += st.session_state["lap_length"]
        temp["end_point"] += st.session_state["lap_length"]
        temp["lap"] += 1
        st.session_state["notes"] = pd.concat([st.session_state["notes"], temp])

    # Dupicate non-lead in (cut to those pre lead, not just filter where type!=lead)
    # Split the above, then join tables <lead> and <laps>*nlaps

    n_rows = st.session_state["notes"].shape[0]

    st.session_state["notes_data_editor"] = st.data_editor(st.session_state["notes"][["highlight", "segment", "start_point","end_point", "notes"]],
                                    hide_index=True, 
                                    height=int(35.2*(n_rows+1)),
                                    use_container_width=False,
                                    column_config={
                                        "highlight":st.column_config.CheckboxColumn("🚨"),
                                        "segment":st.column_config.TextColumn("Segment", width="medium"),
                                        "start_point":st.column_config.NumberColumn("From", format=f"%.2f {st.session_state['d_unit']}", width="small"),
                                        "end_point":st.column_config.NumberColumn("To", format=f"%.2f {st.session_state['d_unit']}", width="small"),
                                        "notes":st.column_config.TextColumn("Notes", width="large")
                                    },
                                    disabled=["segment", "start_point", "end_point", "notes"])
    
    

