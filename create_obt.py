from load_raw.load_obt import load_obt
import duckdb
import os

from dotenv import load_dotenv
load_dotenv()
load_dotenv('variables.env')

load_obt()

with duckdb.connect(os.getenv("DB")) as con:
    print(con.sql("""SELECT * FROM INTERMEDIATE.OBT_FIT""").to_df())