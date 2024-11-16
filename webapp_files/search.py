import streamlit as st 
import fnmatch

strings = ["alpha", "beta", "gamma", "delta", "epsilon", "at", "cat", "cut", "cot", "count", "counted", "counter"]

st.text_input("Search:", key="search_string", help="`?` and `*` are your single and multiple character wildcards")

filtered = []
for search_string in st.session_state["search_string"].replace(", ", ",").split(","):
    if search_string and ('*' not in search_string) and ('?' not in search_string):
        search_string = f"*{search_string}*"
    filtered += [string for string in fnmatch.filter(strings, search_string) if string not in filtered]
    
if len(filtered)>0:
    st.write(filtered)
elif st.session_state["search_string"]:
    st.write(f"Sorry, no hits for {st.session_state['search_string']}!")
else:
    pass