import streamlit as st 
import duckdb

def get_notes():

    with duckdb.connect("data/data.duckdb") as con:
        st.session_state["notes"] = con.sql(f"""SELECT 
                                world, 
                                route, 
                                segment, 
                                type,
                                CASE WHEN type IN ('sprint', 'climb') THEN true ELSE false END AS highlight,
                                start_km/{st.session_state['convert_scale']} AS start_point, 
                                end_km/{st.session_state['convert_scale']} AS end_point, notes 
                            FROM CORE.dim_notes 
                            WHERE world='{st.session_state['world']}' AND route='{st.session_state['route']}'""").to_df()
        
    st.session_state["notes_data_editor"] = st.data_editor(st.session_state["notes"][["highlight", "segment", "start_point","end_point", "notes"]],
                                    hide_index=True, 
                                    use_container_width=False,
                                    column_config={
                                        "highlight":st.column_config.CheckboxColumn("🚨"),
                                        "segment":st.column_config.TextColumn("Segment", width="medium"),
                                        "start_point":st.column_config.NumberColumn("From", format=f"%.2f {st.session_state['d_unit']}", width="small"),
                                        "end_point":st.column_config.NumberColumn("To", format=f"%.2f {st.session_state['d_unit']}", width="small"),
                                        "notes":st.column_config.TextColumn("Notes", width="large")
                                    },
                                    disabled=["segment", "start_point", "end_point", "notes"])
    
    
