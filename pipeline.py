from load.stg_fit import stg_fit
from load.stg_annotations import stg_annotations
from load.dim_fit import dim_fit
from load.dim_annotations import dim_annotations

import duckdb
import os

from dotenv import load_dotenv
load_dotenv()

stg_fit()
stg_annotations()

dim_annotations()
dim_fit()

with duckdb.connect("data/data.duckdb") as con:
    print(con.sql("SHOW ALL TABLES"))
    print(con.sql("SELECT * FROM CORE.DIM_FIT"))
