import os
import psycopg2
import json
from gradient import Gradient
from dotenv import load_dotenv

# Load API Keys
load_dotenv()

# Configuration
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST")
}

# Initialize Gradient (The AI)
client = Gradient(
    model_access_key=os.getenv("MODEL_ACCESS_KEY"),
    workspace_id=os.getenv("GRADIENT_WORKSPACE_ID")
)

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def get_player_state():
    """Fetches the character sheet from Postgres JSONB"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT data FROM game_state WHERE key = 'player_1'")
    result = cur.fetchone()
    conn.close()
    return result[0] if result else {}

def update_hp(new_hp):
    """Example of updating JSONB data"""
    conn = get_db_connection()
    cur = conn.cursor()
    # Postgres JSONB magic: Update just the 'hp' field inside the JSON
    cur.execute("""
        UPDATE game_state 
        SET data = jsonb_set(data, '{hp}', %s) 
        WHERE key = 'player_1'
    """, (str(new_hp),))
    conn.commit()
    conn.close()

def print_aigm_logo():
    # ASCII Art for the Dragon: Using a raw string (r"") to handle backslashes correctly
    dragon_art = r"""
                 \||/
                 |  @___oo
           /\  /\   / (__,,,,|
          ) /^\) ^\/ _)
          )   /^\/   _)
          )   _ /  / _)
      /\  )/\/ ||  | )_)
     <  >      |(,,) )__)
      ||      /    \)___)\
      | \____(      )___) )___
       \______(_______;;; __;;;
    """

    # ASCII Art for 'A.I.G.M.'
    text_art = r"""
        _       ___    _____   __  __ 
       / \     |_ _|  / ____| |  \/  |
      / _ \     | |  | |  __  | \  / |
     / ___ \    | |  | | |_ | | |\/| |
    /_/   \_\  |___|  \_____| |_|  |_|
    """

    print(dragon_art)
    print(text_art)

def run_game_loop():
   # print("--- 🐉 LOCAL DUNGEON MASTER CLI (Ctrl+C to Quit) ---")
    print_aigm_logo()
    
    while True:
        # 1. Get User Input
        user_input = input("\nYOU: ")
        
        # 2. Logic Layer (The "Left Brain")
        # Check for special commands (simple example)
        #== TODO: Set Default Actions Here
        current_state = get_player_state()
        hp = current_state.get('hp', 0)
        
        mechanic_note = ""
        
        if "drink potion" in user_input.lower():
            new_hp = hp + 5
            update_hp(new_hp)
            mechanic_note = f"[System: Player HP increased from {hp} to {new_hp}]"
        elif "attack" in user_input.lower():
             mechanic_note = "[System: Player rolled a 15 (Hit). Enemy takes 6 damage.]"
        
        # 3. Construct Prompt for AI
        prompt = f"""
        [CURRENT STATE]
        Player: {current_state.get('name')}
        HP: {hp}
        Inventory: {current_state.get('inventory')}
        
        [ACTION]
        User said: "{user_input}"
        Game Logic: {mechanic_note}
        
        [TASK]
        Narrate the outcome. Keep it under 50 words. Be atmospheric.
        """

        # 4. Get AI Response
        try:
            response = client.chat.completions.create(
                model="anthropic-claude-opus-4",
                messages=[
                    {"role": "system", "content": "You are a DM. Narrate vividly."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            ai_reply = response.choices[0].message.content
            print(f"\nDM: {ai_reply}")
            
        except Exception as e:
            print(f"\n❌ AI Error: {e}")

if __name__ == "__main__":
    run_game_loop()