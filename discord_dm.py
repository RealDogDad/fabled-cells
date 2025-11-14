import discord
from discord.ext import commands
import random
import sqlite3
import os
from gradient import Gradient
from dotenv import load_dotenv


#-- 1. CONFIGURATION --
# Load the .env file
load_dotenv() #--${{ secrets.API_KEY }}

DISCORD_TOKEN = os.environ.get("${{ secrets.DISCORD_BOT_TOKEN }}")
MODEL_ACCESS_KEY = os.environ.get("${{ secrets.MODEL_ACCESS_KEY }}")
GRADIENT_ID = os.environ.get("${{ secrets.GRADIENT_WORKSPACE_ID }}")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize Gradient SDK
gradient = Gradient()

# 2. THE WORLD BIBLE (In-Context Learning)
# ----------------------------------------
# Since Claude Opus 4 is not fine-tunable by users, we use its massive 200k context window.
# We inject this context into every request.
WORLD_CONTEXT = """
SYSTEM ROLE: You are the Dungeon Master for a gritty Dark Fantasy campaign.
WORLD LORE: The Kingdom of Drakan is under a curse of eternal twilight.
CURRENT SCENE: The players are battling in the Sunken Crypts.
TONE: Visceral, dangerous, and slightly archaic.
"""

# 3. DATABASE SETUP (The State)
# -----------------------------
conn = sqlite3.connect('dnd_state.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS roll_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT,
        die_type TEXT,
        roll_result INTEGER,
        calculated_chance INTEGER
    )
''')
conn.commit()

# 4. THE COMMAND LOGIC
# --------------------
@bot.command(name='roll')
async def roll_dice(ctx):
    user = ctx.author.name
    
    # --- STEP A: LOGIC ENGINE (Python) ---
    die_roll = random.randint(1, 10)
    hit_chance = die_roll * 10 
    
    # --- STEP B: UPDATE STATE (SQL) ---
    cursor.execute(
        "INSERT INTO roll_history (user_name, die_type, roll_result, calculated_chance) VALUES (?, ?, ?, ?)",
        (user, "D10", die_roll, hit_chance)
    )
    conn.commit()
    
    # --- STEP C: PREPARE THE PROMPT ---
    # We construct a prompt that includes the World Context + The Math Result
    prompt_payload = f"""
    {WORLD_CONTEXT}
    
    [GAME EVENT DATA]
    Player: {user}
    Action: Rolled a D10 check
    Result: {die_roll} (on a scale of 1-10)
    Mechanic: {hit_chance}% success rate equivalent.
    
    TASK: Describe the outcome based on the event data. Be brief (max 50 words).
    """

    # --- STEP D: CALL CLAUDE OPUS 4 VIA GRADIENT ---
    try:
        # We get the base model using the specific slug for Opus 4
        # Note: The slug is typically 'anthropic-claude-opus-4' 
        model = gradient.get_base_model(model_slug="anthropic-claude-opus-4")
        
        response = model.complete(
            query=prompt_payload,
            max_generated_token_count=100,
            temperature=0.7
        )
        
        flavor_text = response.generated_output
        
    except Exception as e:
        flavor_text = f"The Dungeon Master is silent (Error: {e})"

    # --- STEP E: REPLY ---
    await ctx.send(flavor_text)

bot.run(DISCORD_TOKEN)