import discord
import gspread
import os
import json
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. GOOGLE SHEETS SETUP ---
# This pulls the JSON from your Railway Environment Variables
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    creds_json = os.getenv('GOOGLE_CREDS')
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # Ensure this name matches your Google Sheet exactly!
    sheet = client.open("Busways Mod Logs").sheet1 
except Exception as e:
    print(f"CRITICAL CONFIG ERROR: {e}")

# --- 2. BOT SETUP ---
class TestBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # This syncs the /test_sheet command so it appears in Discord
        await self.tree.sync()
        print("Slash commands synced successfully.")

bot = TestBot()

# --- 3. THE TEST COMMAND ---
@bot.tree.command(name="test_sheet", description="Verifies the Google Sheets connection")
@app_commands.checks.has_permissions(administrator=True)
async def test_sheet(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True) # Give the bot time to talk to Google
    
    try:
        # 1. Attempt to write a test row
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        test_row = ["TEST_ID", "Tester", "Connection Success!", "System", now]
        sheet.append_row(test_row)
        
        # 2. Immediately find and delete it to keep the sheet clean
        cell = sheet.find("TEST_ID")
        sheet.delete_rows(cell.row)
            
        await interaction.followup.send("✅ **Success!** The bot can read and write to your Google Sheet.")
        print(f"Sheet Test Successful at {now}")
        
    except Exception as e:
        await interaction.followup.send(f"❌ **Connection Failed:** `{e}`")
        print(f"Sheet Test Failed: {e}")

# --- 4. STARTUP ---
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

bot.run(os.getenv('DISCORD_TOKEN'))
