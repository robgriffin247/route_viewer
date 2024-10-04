# RouteViewer

An app to build and view race/route notes for Zwift (and other e-ecycling platforms).

1. Initial design:
    - Load data in from race .fit files into one big table with world and route variables added
    - Create streamlit app to give
        1. Dropdown menus for world and route; route to be reactive to world (routes are a child of world; e.g. Road to Sky only exists in Watopia and should not show if the user selects the Makuri Islands world)
        1. Interactive plot of profile showing distance and altitude including formatted tooltip
        1. Option for miles or km as the units
        1. Generate a summary of the selected area (distance, climbing, average grade)

1. Second phase:
    - Create a csv of route meta-data (start/end points, type and name for leadin, sprint and kom sectors, lap/finish banner) based on distances
    - Generate table with lap capabilities
