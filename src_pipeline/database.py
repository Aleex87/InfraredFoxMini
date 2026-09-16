import time
import os
import psycopg2


# Create connection to TimescaleDB
def get_db_connection():
    max_retries = 5
    retry_delay = 3

    for attempt in range(1, max_retries + 1):
        try:
            return psycopg2.connect(
                host=os.getenv("DB_HOST", "timescaledb"),
                port=5432,
                dbname=os.getenv("POSTGRES_DB", "infrafox"),
                user=os.getenv("POSTGRES_USER", "sensor"),
                password=os.getenv("POSTGRES_PASSWORD"),
            )
        except psycopg2.OperationalError:
            # Stop retrying after the final failed attempt
            if attempt == max_retries:
                raise

            time.sleep(retry_delay)


# Create table for InfraredFox safety events
def create_table():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS safety_events (
        time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        zone TEXT NOT NULL,
        zone_duration DOUBLE PRECISION NOT NULL,
        danger_duration DOUBLE PRECISION NOT NULL
        );
    """)

    connection.commit()
    cursor.close()
    connection.close()


# Store a safety event in TimescaleDB
def insert_event(zone, zone_duration, danger_duration):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO safety_events (zone, zone_duration, danger_duration)
        VALUES (%s, %s, %s);
        """,
        (zone, zone_duration, danger_duration),
    )

    connection.commit()
    cursor.close()
    connection.close()
