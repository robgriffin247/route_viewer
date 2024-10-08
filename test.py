import pandas as pd

sheet_id = "1qHMTUfpi9Gy_l3g9P4umsfdGaJ3O6Bdh9R1yNguoBEc"
sheet_name = "race_notes"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

test = pd.read_csv(url)[["platform", "world", "route", "segment", "type", "start", "end", "note"]]

print(test)