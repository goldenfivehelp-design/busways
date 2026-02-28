import discord
import gspread
import os
import json
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIG ---
GUILD_ID = 1418141167547187312  # Your Server ID
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
class TestBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        # Prefix is still '!' just for the manual sync command
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # This forces the commands to your specific server INSTANTLY
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)
        print(f"Commands synced to Guild: {GUILD_ID}")

bot = TestBot()

# --- THE TEST COMMAND ---
@bot.tree.command(name="test_sheet", description="Verifies the Google Sheets connection")
@app_commands.checks.has_permissions(administrator=True)
async def test_sheet(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        test_row = ["TEST_ID", "Tester", "Connection Success!", "System", now]
        sheet.append_row(test_row)
        
        cell = sheet.find("TEST_ID")
        sheet.delete_rows(cell.row)
            
        await interaction.followup.send("✅ **Success!** Google Sheets is linked.")
    except Exception as e:
        await interaction.followup.send(f"❌ **Failed:** `{e}`")

# --- MANUAL SYNC COMMAND (BACKUP) ---
@bot.command()
@commands.is_owner()
async def sync(ctx):
    await bot.tree.sync(guild=MY_GUILD)
    await ctx.send("Force synced commands to this server.")

bot.run(os.getenv('DISCORD_TOKEN'))
