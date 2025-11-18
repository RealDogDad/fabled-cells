import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Config - In a real app, put these in .env
DB_CONFIG = {
    "dbname": "fabled_cells_db",
    "user": "fabled_admin",
    "password": "aigm_0311",
    "host": "localhost"
}

def init_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 1. Create a table for Game Logs (The Chat History)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS game_logs (
                id SERIAL PRIMARY KEY,
                role VARCHAR(10), -- 'User' or 'DM'
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 2. Create a table for Game State (The "Save File")
        # We use JSONB so we can shove an entire character sheet in one column
        cur.execute("""
            CREATE TABLE IF NOT EXISTS game_state (
                key VARCHAR(50) PRIMARY KEY,
                data JSONB
            );
        """)
        
        # 3. Initialize a default Player State if not exists
        default_char_sheet = '{"name": "Valen", "hp": 20, "inventory": ["Sword", "Torch"]}'
        cur.execute("""
            INSERT INTO game_state (key, data) 
            VALUES ('player_1', %s) 
            ON CONFLICT (key) DO NOTHING;
        """, (default_char_sheet,))

        conn.commit()
        print("✅ Database initialized successfully.")
        
    except Exception as e:
        print(f"❌ Database Error: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    init_db()