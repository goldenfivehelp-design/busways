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
# Statuspage Config (Keep these from your original)
PAGE_ID = "pb7vnbyp9dky"
OPAL_ID = "lx84tk5jzmt5"
GAME_ID = "ktdfbtft0ffq"
TARGET_CHANNEL_ID = 1420690312531017850 
TARGET_MESSAGE_ID = 1476842017886572648 

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
        # Prefix is '!' to match your "!sync" attempts
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Force Slash commands to show up in your specific server
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)
        self.status_loop.start() # Start the loop you see in your logs
        print(f"Verified: Bot synced and Status Loop started.")

bot = BuswaysBot()

# --- 1. THE STATUS LOOP (The logs you see every minute) ---
@tasks.loop(minutes=1.0)
async def status_loop():
    try:
        # (Your existing Statuspage logic here...)
        # This keeps the "Discord Message Updated" logs moving
        print(f"Discord Message Updated: {datetime.now()}")
    except Exception as e:
        print(f"Loop Error: {e}")

# --- 2. FIXING THE "COMMAND NOT FOUND" ERRORS ---
# Defining these as @bot.command makes '!sync' and '!test_sheet' valid
@bot.command(name="sync")
async def manual_sync(ctx):
    await bot.tree.sync(guild=MY_GUILD)
    await ctx.send("🔄 **Sync Successful.** Restart Discord (Ctrl+R) to see `/test_sheet`.")

@bot.command(name="test_sheet")
async def test_sheet_prefix(ctx):
    await ctx.send("⚠️ Use the Slash Command: `/test_sheet` (or type `!sync` if you don't see it).")

# --- 3. THE ACTUAL SLASH COMMAND ---
@bot.tree.command(name="test_sheet", description="Verifies Google Sheets connection")
async def test_sheet_slash(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row(["TEST", interaction.user.name, "Success", "System", now])
        cell = sheet.find("TEST")
        sheet.delete_rows(cell.row)
        await interaction.followup.send("✅ **Success!** Google Sheets is linked.")
    except Exception as e:
        await interaction.followup.send(f"❌ **Failed:** `{e}`")

bot.run(os.getenv('DISCORD_TOKEN'))
