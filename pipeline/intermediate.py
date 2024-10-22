import duckdb
import os

# Much of the logic here is maybe better suited to core, but that's not important enough to move right now

def int_rides():
    with duckdb.connect("data/data.duckdb") as con:
        con.sql(f"CREATE SCHEMA IF NOT EXISTS INTERMEDIATE")

        df = con.sql(f"""
                WITH 
                    SOURCE AS (
                         SELECT 
                            LOWER(REPLACE(CONCAT(world, '__', route), ' ', '_')) AS route_id, 
                            world, route, altitude, distance 
                         FROM STAGING.stg_rides
                    ),

                    ADD_CHANGE AS (
                        SELECT route_id, world, route, altitude, distance,
                            CASE WHEN ROW_NUMBER() OVER() = 1 THEN 0 ELSE altitude - LAG(altitude) OVER() END AS altitude_delta,
                            CASE WHEN ROW_NUMBER() OVER() = 1 THEN 0 ELSE distance - LAG(distance) OVER() END AS distance_delta
                        FROM SOURCE),

                    ADD_GRADIENT AS (
                        SELECT route_id, world, route, altitude, distance,
                            CASE WHEN ROW_NUMBER() OVER() = 1 THEN 0 ELSE altitude_delta/distance_delta*100 END AS gradient
                        FROM ADD_CHANGE),
                    
                    ROLL_GRADIENT AS (
                        SELECT route_id, world, route, altitude, distance,
                            MEAN(gradient) OVER (ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING) AS gradient
                        FROM ADD_GRADIENT)

                SELECT route_id, world, route, altitude, distance, gradient FROM ROLL_GRADIENT""").to_df()
        
        con.sql(f"CREATE OR REPLACE TABLE INTERMEDIATE.int_rides AS SELECT * FROM df")

    print(f"Loaded int_rides")

def int_routes():
    with duckdb.connect("data/data.duckdb") as con:
        df = con.sql("""
                        WITH
                        SOURCE AS (
                            SELECT
                                LOWER(REPLACE(CONCAT(Map, '__', Route), ' ', '_')) AS route_id, 
                                Map AS world,
                                Route AS route,
                                CAST(STR_SPLIT("Lead-in", 'km')[1] AS DECIMAL(10,1)) AS lead,
                                CAST(STR_SPLIT(Length, 'km')[1] AS DECIMAL(10,1)) AS length,
                                CAST(STR_SPLIT(Elevation, 'm')[1] AS DECIMAL(10,1)) AS elevation,
                                NOT CONTAINS(Restriction, 'Run Only') OR Restriction IS NULL AS ride,
                                CONTAINS(Restriction, 'Event Only') AS event
                            FROM STAGING.stg_zi_routes
                        ),

                        NOTES AS (
                            SELECT * EXCLUDE(start_km, end_km),
                                TRY_CAST(REPLACE(start_km, ',', '.') AS FLOAT) AS start_km,
                                TRY_CAST(REPLACE(end_km, ',', '.') AS FLOAT) AS end_km
                            FROM STAGING.stg_notes
                            WHERE type='lead'
                        ),
                     
                        REPLACE_LEAD AS (
                            SELECT * EXCLUDE(lead),
                                CASE WHEN NOTES.end_km NOT NULL THEN end_km ELSE lead END AS lead
                            FROM SOURCE LEFT JOIN NOTES ON SOURCE.world=NOTES.world AND SOURCE.route=NOTES.route
                        ),
                     
                        ADD_TOTAL AS (
                            SELECT *,
                                lead+length AS total_length
                            FROM REPLACE_LEAD
                        )
                     
                        SELECT * FROM ADD_TOTAL
                     """)
        
        con.sql(f"CREATE OR REPLACE TABLE INTERMEDIATE.int_routes AS SELECT * FROM df")

    print(f"Loaded int_routes")


def int_notes():
    with duckdb.connect("data/data.duckdb") as con:
        df = con.sql(f"""
                    WITH SOURCE AS (
                        SELECT 
                            LOWER(REPLACE(CONCAT(world, '__', route), ' ', '_')) AS route_id,
                            * 
                        FROM STAGING.stg_notes 
                    ),
                    
                    CONVERTS AS (
                        SELECT * EXCLUDE(start_km, end_km),
                            TRY_CAST(REPLACE(start_km, ',', '.') AS FLOAT) AS start_point,
                            TRY_CAST(REPLACE(end_km, ',', '.') AS FLOAT) AS end_point
                        FROM SOURCE
                    ),
                     
                    ROUTES AS (
                        SELECT 
                            LOWER(REPLACE(CONCAT(Map, '__', Route), ' ', '_')) AS route_id, 
                            Map AS world,
                            Route AS route,
                            CAST(STR_SPLIT("Lead-in", 'km')[1] AS DECIMAL(10,1)) as lead,
                            CAST(STR_SPLIT(Length, 'km')[1] AS DECIMAL(10,1)) as length
                        FROM STAGING.stg_zi_routes
                        WHERE NOT CONTAINS(Restriction, 'Run Only') OR Restriction IS NULL
                    ),
                     
                    LEAD_LINES AS (
                        SELECT 
                            ROUTES.route_id, ROUTES.world, ROUTES.route, 
                            'Lead in' AS segment,
                            'lead' AS type,
                            CAST(0 AS FLOAT) AS start_point,
                            CAST(lead AS FLOAT) AS end_point,
                            NULL AS note
                        FROM ROUTES 
                        WHERE route_id NOT IN (SELECT route_id FROM CONVERTS)
                    ),

                    FINISH_LINES AS (
                        SELECT 
                            ROUTES.route_id, ROUTES.world, ROUTES.route, 
                            'Finish' AS segment,
                            'finish' AS type,
                            CAST(lead+length AS FLOAT) AS start_point,
                            CAST(lead+length AS FLOAT) AS end_point,
                            NULL AS note
                        FROM ROUTES 
                        WHERE route_id NOT IN (SELECT route_id FROM CONVERTS)
                    ),

                    JOINED_1 AS (
                        (SELECT * FROM LEAD_LINES) UNION
                        (SELECT * FROM FINISH_LINES) 
                    ),
                     
                    JOINED_2 AS (
                        (SELECT * FROM JOINED_1) UNION
                        (SELECT route_id, world, route, segment, type, start_point, end_point, note FROM CONVERTS) 
                    )
                    
                    SELECT * FROM JOINED_2
                    """)

        con.sql(f"CREATE OR REPLACE TABLE INTERMEDIATE.int_notes AS SELECT * FROM df")

    print(f"Loaded int_notes")



def int_notesx():  
    with duckdb.connect("data/data.duckdb") as con:
        df = con.sql("""
                WITH ROAD_DESCRIPTIONS AS (
                SELECT 
                    * EXCLUDE (sector_start, sector_end),
                    CAST(REPLACE(sector_start, ',', '.') AS DECIMAL(10,2)) AS sector_start,
                    CAST(REPLACE(sector_end, ',', '.') AS DECIMAL(10,2)) AS sector_end
                FROM STAGING.stg_road_descriptions
                ),

                ROUTE_ROADS AS (
                SELECT 
                    * EXCLUDE (start),
                    CAST(REPLACE(start, ',', '.') AS DECIMAL(10,2)) AS start,
                FROM STAGING.stg_route_roads
                ),

                JOINED AS (
                SELECT 
                    RR.world, RR.route,
                    RD.sector_name AS segment,
                    RD.sector_type AS type,
                    RD.sector_start + RR.start AS start_point,
                    RD.sector_end + RR.start AS end_point,
                    RD.sector_notes AS note
                FROM ROUTE_ROADS AS RR LEFT JOIN ROAD_DESCRIPTIONS RD ON RR.world=RD.world AND RR.road=RD.road
                )

                SELECT * FROM JOINED ORDER BY world, route, start_point, end_point
                """).to_df()
        
        con.sql(f"CREATE OR REPLACE TABLE INTERMEDIATE.int_notesx AS SELECT * FROM df")

    print(f"Loaded int_notesx")
