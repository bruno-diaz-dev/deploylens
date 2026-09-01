import sqlite3
import os

def get_connection():
    database_path = os.getenv(
        "DEPLOYLENS_DB",
        "deploylens.db"
    )

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    
    return connection

def create_database():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS deployments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT NOT NULL,
            environment TEXT NOT NULL,
            version TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()