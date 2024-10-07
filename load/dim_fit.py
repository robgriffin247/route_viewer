import duckdb
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

def dim_fit():
    with duckdb.connect(os.getenv('DB')) as con:
        fit_data = con.sql("""SELECT F.* FROM STAGING.STG_FIT AS F LEFT JOIN
                           (SELECT PLATFORM, WORLD, ROUTE, "END" AS X FROM STAGING.STG_ANNOTATIONS WHERE TYPE='finish') AS N 
                           ON F.PLATFORM=N.PLATFORM AND
                            F.WORLD=N.WORLD AND
                            F.ROUTE=N.ROUTE
                           WHERE F.DISTANCE/1000<=N.X""").to_df()

        con.sql("""CREATE SCHEMA IF NOT EXISTS CORE""")
        con.sql("""CREATE OR REPLACE TABLE CORE.DIM_FIT AS SELECT * FROM fit_data""")

