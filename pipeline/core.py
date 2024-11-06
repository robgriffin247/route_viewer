import duckdb
import os

def dim_rides():
    with duckdb.connect(f'{os.getenv("data_dir")}/{os.getenv("database")}') as con:
        x = con.sql("""
                      WITH RIDE_LENGTHS AS(
                        SELECT file, world, route, MAX(distance) AS length 
                        FROM INTERMEDIATE.int_rides
                        GROUP BY file, world, route
                      )

                      SELECT A.world, A.route, A.length, B.total AS expected_min, A.file
                      FROM RIDE_LENGTHS AS A LEFT JOIN 
                          (SELECT world, route, total FROM INTERMEDIATE.int_routes) AS B ON
                          A.world=B.world AND A.route=B.route
                      WHERE length<total
                      """).to_df()
        if x.shape[0] > 0:
            raise Exception("\n" + "="*80 + f"\n\nRide data too short, check file(s)/ride_lengths: \n{x}")

        df = con.sql("""
                    WITH RIDES AS (
                        SELECT * FROM INTERMEDIATE.int_rides
                    ),

                    ROUTES AS (
                        SELECT world, route, lead, total
                        FROM INTERMEDIATE.int_routes
                    ),
                     
                    TRIM_RIDES AS (
                        SELECT A.* 
                        FROM RIDES AS A LEFT JOIN ROUTES AS B ON A.world=B.world AND A.route=B.route
                        WHERE A.distance<=B.total
                    ),
                    
                    ADD_LAP AS(
                        SELECT A.*, 
                            CASE WHEN A.distance<B.lead THEN 0 ELSE 1 END AS lap
                        FROM TRIM_RIDES AS A LEFT JOIN ROUTES AS B ON A.world=B.world AND A.route=B.route
                    )
                     
                    SELECT world, route, lap, longitude, latitude, distance, altitude, gradient FROM ADD_LAP 
                    """)
        con.sql('CREATE OR REPLACE TABLE CORE.dim_rides AS SELECT * FROM df')

def dim_notes():
    with duckdb.connect(f'{os.getenv("data_dir")}/{os.getenv("database")}') as con:
        df = con.sql("""
                     WITH SECTOR_DESCRIPTIONS AS (
                        SELECT * FROM INTERMEDIATE.int_sector_descriptions
                     ),
                     
                     ROUTE_SECTORS AS (
                        SELECT * FROM INTERMEDIATE.int_route_sectors
                     ),
                     
                     ROUTES AS (
                        SELECT * FROM INTERMEDIATE.int_routes
                     ),

                     CORRECT_STARTS AS (
                        SELECT A.* EXCLUDE(sector_start),
                            A.sector_start + B.gpx_correction AS sector_start
                        FROM ROUTE_SECTORS AS A LEFT JOIN ROUTES AS B ON A.world=B.world AND A.route=B.route
                     ),

                     ROUTE_DESCRIPTIONS AS (
                        SELECT A.world, A.route,
                            B.note_name AS segment,
                            A.sector_start + B.note_start AS start_point,
                            A.sector_start + B.note_end AS end_point,
                            B.note_type AS type, 
                            B.note_description AS note
                        FROM CORRECT_STARTS AS A LEFT JOIN SECTOR_DESCRIPTIONS AS B ON A.sector_id=B.sector_id
                     ),

                     SORTED AS (
                        SELECT * FROM ROUTE_DESCRIPTIONS
                        ORDER BY world, route, start_point, end_point DESC
                     ),

                     CLEAR_NAME AS (
                        SELECT * EXCLUDE(segment),
                            CASE WHEN LAG(segment) OVER()=segment THEN '' ELSE segment END AS segment
                        FROM SORTED
                        ORDER BY world, route, start_point, end_point DESC

                     )

                     SELECT world, route, segment, start_point, end_point, type, note FROM CLEAR_NAME
                     """)
        
        con.sql("CREATE OR REPLACE TABLE CORE.dim_notes AS SELECT * FROM df")
        # Merge sector_descriptions and route_sectors


def dim_routes():
    with duckdb.connect(f'{os.getenv("data_dir")}/{os.getenv("database")}') as con:
        df = con.sql("SELECT world, route, lead, total-lead AS lap, circuit, complete_notes FROM INTERMEDIATE.int_routes")
        con.sql("CREATE OR REPLACE TABLE CORE.dim_routes AS SELECT * FROM df")
