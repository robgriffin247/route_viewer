import streamlit as st 
 
page_config = st.secrets["page_config"]

st.markdown(f"""
The objective of this app is to create **race-ready route notes describing key the sections of popular Zwift racing routes**. Most importantly, {page_config["page_name"]} provides

- an **interactive route profile**, allowing users to zoom, scroll and explore the route profile
- detailed and concise **notes for critical parts of the route** &mdash; not just where to find sprint and kom segments          
- funcionality to **set the number of laps**, updating the route profile and race notes to make it easy to describe the whole route, not just the first lap!
- outputs in **metric or imperial**

----------
            
{page_config["page_name"]} is developed by Rob Griffin &mdash; data engineer by day and keen zwifter by night! 
Follow me on [instagram](https://www.instagram.com/griffin_cycling/) for updates. 
Special thanks to the [Tea & Scone club](https://www.facebook.com/TeaSconeBikes) on Zwift who have helped develop and test this project.
            
It is early days for this project and I am currently working to build the data, 
but it takes time &mdash; each route requires ride data and annotating. 
That involves watching races on YouTube and repeatedly watching the key sections to create a thorough and accurate description.

Finding this app useful? I've made it to be fully open and free to use, but if you'd like to make a donation then head over to [buymeacoffee](https://buymeacoffee.com/griffin_cycling).
With enough donations, I might even get to upgrade my 15 year old Specialized Allez! Every donation is hugely appreciated and helps keep me motivated to invest my time and expertise :) 
            
Ride on!
""")