import streamlit as st 

def get_notes_table():
    st.session_state["notes_data_editor"] = st.data_editor(st.session_state["notes_data"][["segment", "type", "highlight", "start_point", "end_point", "note"]],
                   hide_index=True, 
                   height=int(35.2*(st.session_state["notes_data"].shape[0]+1)),
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
    
