from pipeline.staging import stg_fits, stg_sheets
from pipeline.intermediate import int_fits, int_notes, int_routes
from pipeline.core import dim_fits, dim_notes, dim_routes

stg_fits()
stg_sheets(refresh=True)

int_fits()
int_notes()
int_routes()

dim_fits()
dim_notes()
dim_routes()
