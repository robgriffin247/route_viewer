import streamlit as st 
from app_files.route_menu import route_menu
from app_files.lap_menu import lap_menu
from app_files.get_notes import get_notes
from app_files.get_plot import get_plot

st.set_page_config(
    page_title="RouteViewer",
    page_icon=":bike:"
)

st.title("RouteViewer")
st.write("Racing Notes for Zwift")
st.html("<hr/>")

route_menu()
profile_plot_cont = st.container()
lap_menu()
get_notes()
get_plot()
profile_plot_cont.plotly_chart(st.session_state["profile_plot"])


st.html("""
<style>
    .subtle { color: #4f6360; 
        font-weight: 300;}
    .subtle_link { color: #478f84; }
</style>
<br/>
<br/>
<hr/>
<p class="subtle">RouteViewer is developed by Rob Griffin &mdash; data engineer by day and keen zwifter by night! Follow me on instagram <a class="subtle_link" href=="https://www.instagram.com/griffin_cycling/">@griffin_cycling</a> for updates.</p>
            
<p class="subtle">It is early days for this project and I am currently working to build the data, but it takes time &mdash; each route requires riding and annotating. This involves riding the route myself or sending a bot around the route to get <em>.fit</em> data, and trawling through race videos on YouTube to develop notes. It takes time and money!</p>

<p class="subtle">To support the project, to help cover costs (like the hardware and Zwift membership needed to run bots) or just to give me a bit of motivation, then head over to <a class="subtle_link" href="https://buymeacoffee.com/griffin_cycling">buymeacoffee</a>!</p>
""")