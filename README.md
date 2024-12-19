# RouteViewer

This app is designed to combine .gpx files from activities on Zwift (and other e-cycling platforms in the future) with route descriptions/racing notes. For routes that can be lapped (lead-in ends/route starts where the route finishes - it is a circuit; e.g. Glasgow Crit, e.g. not Road to Sky which starts in the jungle and finishes atop the alpe) it also allows users to set the number of laps, adjusting the route profile graph and table of notes accordingly. Users can also set metric (km/metres) or imperial (miles/feet).

The route profile graph is interactive, allowing users to zoom in and out of sections, scroll axes and hover over the line to get details about distance, altitude and gradient. Users can also highlight specific notes on the profile graph, with KOM/sprint segments automatically shown by default (and coloured appropriately).

### TODO 

- Check if route covered by >1 gpx file before running pipeline
- Create check in stg_rides to cause omit dataset & message about if length < total length in ZI note
- Put logic of table of routes with no gpx data into pipeline (dim_todo) then read into data_page.py
- Create table (dim_basic) of routes with no detailed notes - add to data_page.py
- Create upload feature in data_page.py; check if route needed
- Focus work on notes to id routes that can be lapped (then reinstate can_lap flow control)





- [x] task 1
- [ ] task 2
