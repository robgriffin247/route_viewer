from pipeline.staging import stg_fits, stg_notes
from pipeline.intermediate import int_fits, int_notes, int_routes
from pipeline.core import dim_fits, dim_notes, dim_routes

v = False

stg_fits(verbose=v)
stg_notes(refresh=True, verbose=v)

int_fits(verbose=v)
int_notes(verbose=v)
int_routes(verbose=v)

dim_fits(verbose=v)
dim_notes(verbose=v)
dim_routes(verbose=v)
