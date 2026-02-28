import discord
import gspread
import os
import json
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIG ---
GUILD_ID = 1418141167547187312 
MY_GUILD = discord.Object(id=GUILD_ID)

# --- GOOGLE SHEETS SETUP ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
try:
    creds_json = os.getenv('GOOGLE_CREDS')
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open("Busways Mod Logs").sheet1 
except Exception as e:
    print(f"DATABASE ERROR: {e}")

# --- BOT SETUP ---
class BuswaysBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # This is the magic part for / commands.
        # It copies your code's commands and uploads them to your specific Discord server.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)
        print(f"Slash commands synced to {GUILD_ID}")

bot = BuswaysBot()

# --- THE SLASH COMMAND (/test_sheet) ---
@bot.tree.command(name="test_sheet", description="Test the Google Sheet connection")
async def test_sheet(interaction: discord.Interaction):
    # Slash commands use 'interaction' instead of 'ctx'
    await interaction.response.defer(ephemeral=True) # Tells Discord the bot is thinking
    
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row(["TEST", interaction.user.name, "Success", "Bot", now])
        
        cell = sheet.find("TEST")
        sheet.delete_rows(cell.row)
            
        await interaction.followup.send("✅ **Success!** The Slash Command and Google Sheet are linked.")
    except Exception as e:
        await interaction.followup.send(f"❌ **Failed:** `{e}`")

bot.run(os.getenv('DISCORD_TOKEN'))
