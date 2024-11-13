import streamlit as st 

strings = ["alpha", "beta", "gamma", "delta", "alpha gamma"]

st.text_input("Search:", key="search_string")

focal_strings = [string for string in strings if st.session_state["search_string"].lower() in string.lower()]

st.write(focal_strings)