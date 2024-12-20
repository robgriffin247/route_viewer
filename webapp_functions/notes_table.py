import streamlit as st


def notes_table():
    st.session_state["notes_focal"] = st.session_state["notes_focal"].sort(
        ["note_start", "note_type", "note_end"], nulls_last=True
    )

    if st.session_state["notes_focal"].height > 0:
        st.session_state["live_notes"] = st.data_editor(
            st.session_state["notes_focal"][
                [
                    "highlight",
                    "note_title",
                    "note_type",
                    "note_start",
                    "note_end",
                    "note",
                ]
            ],
            hide_index=True,
            use_container_width=True,
            column_config={
                "highlight": st.column_config.CheckboxColumn("🚨"),
                "note_title": st.column_config.TextColumn("Segment", width="medium"),
                "note_type": None,
                "note_start": st.column_config.NumberColumn(
                    "From",
                    format=f"%.2f {st.session_state['dst_units']}",
                    width="small",
                ),
                "note_end": st.column_config.NumberColumn(
                    "To", format=f"%.2f {st.session_state['dst_units']}", width="small"
                ),
                "note": st.column_config.TextColumn("Note", width="large"),
            },
        )
        #st.write(st.session_state["routes_focal"])

    else:
        st.write(
            "Apologies. Notes have not yet been created for this route! I am working to generate new notes all the time but it involves a lot of work in my limited spare time. Please check back soon or reach out to me to request the notes; I will prioritise the most requested."
        )
