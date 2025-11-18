import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

class FabledBot(commands.Bot):
    def __init__(self):
        # Setup intents
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # This loads the 'cogs' folder extensions
        await self.load_extension("cogs.gameplay")
        # This syncs the slash commands (/) to Discord
        await self.tree.sync()
        print("✅ Cogs loaded and Commands synced!")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

bot = FabledBot()
bot.run(TOKEN)