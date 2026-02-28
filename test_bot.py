import discord
from discord import app_commands
from discord.ext import commands
import os

# --- HARDCODED CONFIG ---
MY_GUILD = discord.Object(id=1418141167547187312)
MY_APP_ID = 1476833993671446628 

class BuswaysBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        # We pass the application_id directly here
        super().__init__(
            command_prefix="!", 
            intents=intents, 
            application_id=MY_APP_ID
        )

    async def setup_hook(self):
        print("Attempting to sync commands...")
        # This pushes your commands to the Discord sidebar menu
        self.tree.copy_global_to(guild=MY_GUILD)
        synced = await self.tree.sync(guild=MY_GUILD)
        print(f"✅ SUCCESS: Synced {len(synced)} commands to Server {MY_GUILD.id}")

bot = BuswaysBot()

# --- THE COMMAND ---
@bot.tree.command(name="test_sheet", description="Check if slash commands work")
async def test_sheet(interaction: discord.Interaction):
    await interaction.response.send_message("🚀 **Slash commands are WORKING!**", ephemeral=True)

# --- STATUS LOG (To match your logs) ---
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print(f'Discord Message Updated: {discord.utils.utcnow()}')

bot.run(os.getenv('DISCORD_TOKEN'))
