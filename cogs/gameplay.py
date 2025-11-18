import discord
from discord import app_commands
from discord.ext import commands

class Gameplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- 1. THE UNIVERSAL ROLL ---
    @app_commands.command(name="roll", description="Roll any dice expression (e.g., 1d20+5)")
    async def roll(self, interaction: discord.Interaction, expression: str):
        # STUB: No logic, just echo
        await interaction.response.send_message(f"🎲 **STUB:** You want to roll: `{expression}`")

    # --- 2. COMBAT ACTIONS ---
    @app_commands.command(name="attack", description="Make a weapon attack")
    async def attack(self, interaction: discord.Interaction, weapon: str, target: str):
        await interaction.response.send_message(f"⚔️ **STUB:** Attacking {target} with {weapon}.")

    @app_commands.command(name="magic", description="Cast a spell (D&D 2024 Magic Action)")
    async def magic(self, interaction: discord.Interaction, spell: str, level: int = 1):
        await interaction.response.send_message(f"✨ **STUB:** Casting {spell} at Level {level}.")

    # --- 3. MOVEMENT & DEFENSE ---
    @app_commands.command(name="dash", description="Gain extra movement for the turn")
    async def dash(self, interaction: discord.Interaction):
        await interaction.response.send_message("💨 **STUB:** Action: DASH (Movement doubled).")

    @app_commands.command(name="disengage", description="Prevent Opportunity Attacks")
    async def disengage(self, interaction: discord.Interaction):
        await interaction.response.send_message("🛡️ **STUB:** Action: DISENGAGE (Safe movement).")

    @app_commands.command(name="dodge", description="Impose disadvantage on attackers")
    async def dodge(self, interaction: discord.Interaction):
        await interaction.response.send_message("🥋 **STUB:** Action: DODGE (Defense stance).")

    # --- 4. UTILITY & SKILLS ---
    @app_commands.command(name="check", description="Roll a Skill Check")
    @app_commands.choices(skill=[
        app_commands.Choice(name="Perception", value="perception"),
        app_commands.Choice(name="Stealth", value="stealth"),
        app_commands.Choice(name="Athletics", value="athletics"),
        # Add more D&D 2024 skills here...
    ])
    async def check(self, interaction: discord.Interaction, skill: app_commands.Choice[str]):
        await interaction.response.send_message(f"👁️ **STUB:** Skill Check for: {skill.name}")

    @app_commands.command(name="utilize", description="Interact with an object (D&D 2024 Utilize Action)")
    async def utilize(self, interaction: discord.Interaction, object_name: str):
        await interaction.response.send_message(f"✋ **STUB:** Action: UTILIZE on {object_name}.")

# This function is required for the bot to load this file
async def setup(bot):
    await bot.add_cog(Gameplay(bot))