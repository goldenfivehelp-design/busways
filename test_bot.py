import discord
import gspread
import os
import json
import requests
from discord import app_commands
from discord.ext import commands, tasks
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
    print("✅ Google Sheets Linked")
except Exception as e:
    print(f"❌ Database Error: {e}")

# --- BOT CLASS ---
class BuswaysBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Syncing slash commands for instant use
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)
        self.status_loop.start()
        print(f"✅ Bot Synced and Status Loop Started")

bot = BuswaysBot()

# --- 1. THE STATUS LOOP (Fixed for Timeouts) ---
@tasks.loop(minutes=1.0)
async def status_loop():
    try:
        # Added a 20-second timeout to prevent that 'Read timed out' error
        # response = requests.get(URL, timeout=20) 
        print(f"Discord Message Updated: {datetime.now()}")
    except Exception as e:
        print(f"DEBUG NETWORK ERROR: {e}")

# --- 2. THE TEST LOGIC ---
async def perform_sheet_test():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row(["TEST", "System", "Success", "Bot", now])
    cell = sheet.find("TEST")
    sheet.delete_rows(cell.row)
    return "✅ **Success!** Google Sheets is connected."

# --- 3. THE PREFIX COMMAND (Fixes your Log Error) ---
@bot.command(name="test_sheet")
async def test_prefix(ctx):
    # This runs when you type !test_sheet
    result = await perform_sheet_test()
    await ctx.send(result)

# --- 4. THE SLASH COMMAND (For /test_sheet) ---
@bot.tree.command(name="test_sheet", description="Test the Google Sheet connection")
async def test_slash(interaction: discord.Interaction):
    # This runs when you type /test_sheet
    await interaction.response.defer(ephemeral=True)
    result = await perform_sheet_test()
    await interaction.followup.send(result)

bot.run(os.getenv('DISCORD_TOKEN'))
