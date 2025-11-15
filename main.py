import os
import psycopg2
import json
from gradient import Gradient
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()

# Database Configuration (Matches your .env)
DB_CONFIG = {
    "dbname": os.environ.get("DB_NAME"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASS"),
    "host": os.environ.get("DB_HOST")
}

# Initialize Gradient (The AI)
try:
    client = Gradient(
        model_access_key=os.environ.get("MODEL_ACCESS_KEY"),
        workspace_id=os.environ.get("GRADIENT_WORKSPACE_ID")
    )
except Exception as e:
    print(f"⚠️ Gradient Config Error: {e}")
    client = None

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def get_player_state():
    """Fetches the character sheet from Postgres JSONB"""
    conn = get_db_connection()
    cur = conn.cursor()
    # We use the key 'player_1' (created in db_setup.py)
    cur.execute("SELECT data FROM game_state WHERE key = 'player_1'")
    result = cur.fetchone()
    conn.close()
    return result[0] if result else {}

def update_hp(new_hp):
    """Updates just the HP field in the JSONB blob"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE game_state 
        SET data = jsonb_set(data, '{hp}', %s) 
        WHERE key = 'player_1'
    """, (str(new_hp),))
    conn.commit()
    conn.close()

def run_game_loop():
    print("\n==========================================")
    print("   🐉 FABLED CELLS: LOCAL CLI TEST")
    print("   (Type 'quit' to exit)")
    print("==========================================\n")
    
    while True:
        try:
            # 1. Get User Input
            user_input = input("YOU: ")
            if user_input.lower() in ['quit', 'exit']:
                print("Exiting...")
                break
            
            # 2. Logic Layer (The "Left Brain")
            current_state = get_player_state()
            hp = current_state.get('hp', 0)
            name = current_state.get('name', 'Hero')
            
            mechanic_note = ""
            
            # Simple Logic Triggers for Testing
            if "potion" in user_input.lower():
                new_hp = hp + 10
                update_hp(new_hp)
                mechanic_note = f"[SYSTEM: HEALING. HP updated from {hp} to {new_hp}]"
                hp = new_hp # Update local var for prompt
            elif "attack" in user_input.lower():
                 mechanic_note = "[SYSTEM: COMBAT. Player rolled 18 (Hit). Enemy takes 8 damage.]"
            else:
                mechanic_note = "[SYSTEM: NARRATIVE ONLY. No stat changes.]"
            
            # 3. Construct Prompt for AI
            prompt = f"""
            [CURRENT SAVE FILE]
            Player: {name} | HP: {hp} | Inventory: {current_state.get('inventory')}
            
            [ACTION]
            User Input: "{user_input}"
            Game Logic Result: {mechanic_note}
            
            [TASK]
            Narrate the outcome based on the Logic Result. 
            Tone: Dark Fantasy. Length: Under 50 words.
            """

            # 4. Get AI Response
            print("   (Thinking...)")
            response = client.chat.completions.create(
                model="anthropic-claude-opus-4",
                messages=[
                    {"role": "system", "content": "You are the Dungeon Master."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            ai_reply = response.choices[0].message.content
            print(f"\nDM: {ai_reply}\n")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    run_game_loop()