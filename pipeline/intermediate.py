import duckdb
import os


def int_rides():
    with duckdb.connect(f'{os.getenv("data_dir")}/{os.getenv("database")}') as con:
        df = con.sql("""
                WITH 
                -- Get the change in distance/altitude from row to row     
                CHANGES AS (
                    SELECT *,     
                        CASE WHEN ROW_NUMBER() OVER() = 1 THEN 0 ELSE LAG(distance) OVER()-distance END AS distance_change,
                        CASE WHEN ROW_NUMBER() OVER() = 1 THEN 0 ELSE LAG(altitude) OVER()-altitude END AS altitude_change
                    FROM STAGING.stg_rides
                ),
                
                -- Smooth the changes out by taking average over 3 rows
                SMOOTH_CHANGES AS (
                    SELECT file, world, route, distance, altitude,
                        CASE WHEN ROW_NUMBER() OVER() = 1 THEN 0 ELSE 
                            SUM(altitude_change) OVER(ROWS 2 PRECEDING) / SUM(distance_change) OVER(ROWS 2 PRECEDING) / 0.01 END AS gradient
                    FROM CHANGES        
                ),
                
                METRES AS (
                    SELECT * EXCLUDE(distance), distance/1000 AS distance FROM SMOOTH_CHANGES
                )
            
                SELECT * FROM METRES
                """)
        
        con.sql("CREATE OR REPLACE TABLE INTERMEDIATE.int_rides AS SELECT * FROM df")

def int_routes():
    with duckdb.connect(f'{os.getenv("data_dir")}/{os.getenv("database")}') as con:
        df = con.sql("""
                WITH 
                -- Routes from ZwiftInsider contain lead in and total lengths for all routes; remove run routes
                ZI_ROUTES AS (
                    SELECT
                        Map AS world,
                        Route AS route,
                        CAST(STR_SPLIT("Lead-in", 'km')[1] AS FLOAT) AS lead,
                        CAST(STR_SPLIT("Lead-in", 'km')[1] AS FLOAT) + CAST(STR_SPLIT(Length, 'km')[1] AS FLOAT) as total,
                        NULL AS circuit,
                        NULL AS gpx_correction,
                        NULL AS complete_notes
                    FROM STAGING.stg_routes
                    WHERE NOT CONTAINS(Restriction, 'Run Only') OR Restriction IS NULL
                ),
            
                -- More precise, and contains gpx correction; notes are made by watching videos of races but gpx starts after departing pens
                MY_ROUTES AS (
                    SELECT 
                        world, route, lead, total, circuit, 
                        CASE WHEN CONTAINS(gpx_correction, '−') THEN 
                            -CAST(REPLACE(REPLACE(gpx_correction, '−', ''), ',', '.') AS FLOAT) ELSE
                            CAST(REPLACE(gpx_correction, ',', '.') AS FLOAT) END AS gpx_correction,
                        complete_notes
                    FROM STAGING.stg_route_lengths       
                ),

                -- Correct lead in and total lengths taken from video notes     
                CORRECTION AS (
                    SELECT 
                        world, route,
                        CAST(REPLACE(lead, ',', '.') AS FLOAT) + gpx_correction AS lead,
                        CAST(REPLACE(total, ',', '.') AS FLOAT) + gpx_correction AS total,
                        circuit,
                        gpx_correction,
                        complete_notes
                    FROM MY_ROUTES     
                ),

                APPENDED AS (
                    (SELECT * FROM CORRECTION) UNION
                    (SELECT * FROM ZI_ROUTES WHERE CONCAT(world, '_', route) NOT IN (SELECT CONCAT(world, '_', route) FROM MY_ROUTES))
                )
                     
                SELECT * FROM APPENDED
                """)
        
        con.sql('CREATE OR REPLACE TABLE INTERMEDIATE.int_routes AS SELECT * FROM df')

def int_sector_descriptions():
    with duckdb.connect(f'{os.getenv("data_dir")}/{os.getenv("database")}') as con:
        df = con.sql("""
                    WITH DESCRIPTIONS AS (
                        SELECT * EXCLUDE(note_start_km, note_end_km, note_type),
                            CASE WHEN note_type IS NOT NULL THEN note_type ELSE 'other' END AS note_type,
                            CAST(REPLACE(note_start_km, ',', '.') AS DOUBLE) AS note_start,
                            CAST(REPLACE(note_end_km, ',', '.') AS DOUBLE) AS note_end
                        FROM STAGING.stg_sector_descriptions
                    )
                    
                    SELECT * FROM DESCRIPTIONS""")

        con.sql("CREATE OR REPLACE TABLE INTERMEDIATE.int_sector_descriptions AS SELECT * FROM df")

def int_route_sectors():
    with duckdb.connect(f'{os.getenv("data_dir")}/{os.getenv("database")}') as con:
        df = con.sql("""
                    WITH SECTORS AS (
                        SELECT world, route, sector_id,
                            CAST(REPLACE(sector_start, ',', '.') AS FLOAT) AS sector_start
                        FROM STAGING.stg_route_sectors
                        WHERE world IS NOT NULL
                    )
                     
                    SELECT * FROM SECTORS""")

        con.sql("CREATE OR REPLACE TABLE INTERMEDIATE.int_route_sectors AS SELECT * FROM df")