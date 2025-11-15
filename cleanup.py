import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

# We must connect to the 'postgres' system database to drop our app database.
# You cannot be inside the house while you are demolishing it.
SYSTEM_DB_CONFIG = {
    "dbname": "postgres", # Connect to system DB
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASS"),
    "host": os.environ.get("DB_HOST")
}

TARGET_DB = os.environ.get("DB_NAME")

def destroy_database():
    print(f"⚠️  WARNING: About to DESTROY database '{TARGET_DB}'.")
    confirm = input("Type 'DESTROY' to confirm: ")
    
    if confirm != "DESTROY":
        print("❌ Aborted.")
        return

    conn = None
    try:
        # 1. Connect to the System DB
        conn = psycopg2.connect(**SYSTEM_DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # 2. Terminate existing connections (The "Kick" command)
        # If we don't do this, the DROP command will fail if the app is running.
        print(f"🔌 Disconnecting active users from {TARGET_DB}...")
        cur.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{TARGET_DB}'
            AND pid <> pg_backend_pid();
        """)

        # 3. Drop the Database
        print(f"💥 Dropping {TARGET_DB}...")
        cur.execute(f"DROP DATABASE IF EXISTS {TARGET_DB};")
        
        print("✅ Database destroyed successfully.")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Tip: Ensure 'fabled_admin' has permission to connect to 'postgres' database.")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    destroy_database()