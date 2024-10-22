import duckdb

def too_short():
    with duckdb.connect("data/data.duckdb") as con:
        
        too_short = con.sql("""
                    WITH NOTES AS (
                        SELECT * FROM INTERMEDIATE.int_notes WHERE type in ('finish', 'lap_banner') 
                    ),
                    RIDES AS (
                        SELECT route_id, MAX(distance)/1000 AS total 
                        FROM INTERMEDIATE.int_rides
                        GROUP BY route_id
                    ),
                    TOO_SHORT AS (
                        SELECT RIDES.route_id, RIDES.total, NOTES.end_point
                        FROM RIDES LEFT JOIN NOTES ON RIDES.route_id=NOTES.route_id
                        WHERE RIDES.total < NOTES.end_point
                    )
                    SELECT * 
                    FROM TOO_SHORT
                    """)

        print("The following gpx files did not cover the entire route - remove them and find a new source:")
        print(too_short)
        print("="*80)
        print(" "*80)


def to_get():
    with duckdb.connect("data/data.duckdb") as con:
        df = con.sql("""
                    WITH GPXs AS (
                        SELECT DISTINCT(world, route) AS id FROM CORE.dim_rides
                    ),
                    ROUTES AS (
                        SELECT DISTINCT(world, route) AS id FROM INTERMEDIATE.int_routes
                    )
                    SELECT * FROM ROUTES WHERE id NOT IN (SELECT * FROM GPXs)
                    """)
        print(df)