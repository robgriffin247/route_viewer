import duckdb
import os

def dim_rides():
    with duckdb.connect("data/data.duckdb") as con:
        df = con.sql(f"""WITH
                        RIDES AS (
                            SELECT *
                            FROM INTERMEDIATE.int_rides
                        ),
                     
                        LEADS AS (
                            SELECT route_id, end_point
                            FROM INTERMEDIATE.int_notes
                            WHERE type='lead'
                        ),

                        FINISHES AS (
                            SELECT route_id, end_point
                            FROM INTERMEDIATE.int_notes
                            WHERE type IN ('finish', 'lap_banner')
                        ),
                     
                        ADD_LAPS AS (
                            SELECT 
                                RIDES.*,
                                CASE WHEN RIDES.distance < (LEADS.end_point*1000) THEN  0 ELSE 1 END AS lap
                            FROM RIDES LEFT JOIN LEADS ON RIDES.route_id=LEADS.route_id
                        ),

                        CUT_FINISH AS (
                            SELECT *
                            FROM ADD_LAPS LEFT JOIN FINISHES ON ADD_LAPS.route_id=FINISHES.route_id
                            WHERE ADD_LAPS.distance <= (FINISHES.end_point*1000)
                        )

                        SELECT * FROM CUT_FINISH
                        """)
                
        con.sql("CREATE OR REPLACE TABLE CORE.dim_rides AS SELECT * FROM df")

    print("Loaded dim_rides")

def dim_notes():
    with duckdb.connect("data/data.duckdb") as con:
        df = con.sql(f"""WITH SOURCE AS (
                        SELECT * FROM INTERMEDIATE.int_notes
                     )
                     SELECT * FROM SOURCE
                     """)
        con.sql("CREATE OR REPLACE TABLE CORE.dim_notes AS SELECT * FROM df")

def dim_notesx():
    with duckdb.connect("data/data.duckdb") as con:
        df = con.sql(f"""WITH SOURCE AS (
                        SELECT * FROM INTERMEDIATE.int_notesx
                     )
                     SELECT * FROM SOURCE
                     """)
        con.sql("CREATE OR REPLACE TABLE CORE.dim_notesx AS SELECT * FROM df")
