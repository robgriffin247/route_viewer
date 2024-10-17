import streamlit as st 

st.html("""
<style>
    .subtle_link { color: #478f84; }
</style>

<p class="subtle">RouteViewer is developed by Rob Griffin &mdash; data engineer by day and keen zwifter by night! 
        Follow me on instagram <a class="subtle_link" href=="https://www.instagram.com/griffin_cycling/">@griffin_cycling</a> for updates. 
        Special thanks to the <a class="subtle_link" href="https://www.facebook.com/TeaSconeBikes">Tea & Scone club</a> on Zwift who have helped 
        develop and test this project.</p>
            
<p class="subtle">It is early days for this project and I am currently working to build the data, 
        but it takes time &mdash; each route requires riding and annotating. This involves riding the route 
        myself or sending a bot around the route to get <em>.fit</em> data, and trawling through race videos on YouTube to develop notes. 
        It takes time and money!</p>

<p class="subtle">To support the project, to help cover costs (like the hardware and Zwift membership needed to run bots) or 
        just to give me a bit of motivation, then head over to <a class="subtle_link" href="https://buymeacoffee.com/griffin_cycling">buymeacoffee</a> 
        &mdash; if you're feeling really generous you can even buy me a bike 😉</p> 
""")