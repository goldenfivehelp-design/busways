import discord
import gspread
import os
import json
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURATION ---
GUILD_ID = 1418141167547187312  # Your Server ID
MY_GUILD = discord.Object(id=GUILD_ID)

# --- GOOGLE SHEETS SETUP ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    # Ensure 'GOOGLE_CREDS' is the name of your Railway Variable
    creds_json = os.getenv('GOOGLE_CREDS')
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    # Ensure this matches your Sheet title exactly
    sheet = client.open("Busways Mod Logs").sheet1 
    print("Google Sheets Connection: Initialized")
except Exception as e:
    print(f"CRITICAL DATABASE ERROR: {e}")

# --- BOT SETUP ---
class BuswaysTestBot(commands.Bot):
    def __init__(self):
        # Intents must be enabled in Discord Developer Portal
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        """This runs before the bot starts listening for events."""
        # 1. Clear global commands to avoid duplicates
        # 2. Sync to your specific guild for INSTANT results
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)
        print(f"Sync complete for Guild: {GUILD_ID}")

bot = BuswaysTestBot()

# --- 1. THE SLASH COMMAND TEST ---
@bot.tree.command(name="test_sheet", description="Verifies the Google Sheets connection")
@app_commands.checks.has_permissions(administrator=True)
async def test_sheet(interaction: discord.Interaction):
    """Writes a row to Google Sheets and deletes it to verify Editor perms."""
    await interaction.response.defer(ephemeral=True)
    
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        test_data = ["TEST_ID", interaction.user.name, "Connection Success!", "Bot System", now]
        
        # Write to sheet
        sheet.append_row(test_data)
        
        # Cleanup: Find the row we just made and delete it
        cell = sheet.find("TEST_ID")
        sheet.delete_rows(cell.row)
            
        await interaction.followup.send("✅ **Verified!** The bot successfully wrote to and cleaned up the Google Sheet.")
    except Exception as e:
        await interaction.followup.send(f"❌ **Error:** `{e}`\nCheck if the Sheet is shared with the client_email.")

# --- 2. THE MANUAL SYNC (PREFIX COMMAND) ---
@bot.command(name="sync")
async def manual_sync(ctx):
    """A backup command in case Slash commands don't appear."""
    if ctx.author.id == ctx.guild.owner_id or ctx.author.guild_permissions.administrator:
        await bot.tree.sync(guild=MY_GUILD)
        await ctx.send("🔄 Force-synced slash commands to this server. Try /test_sheet now.")

# --- STARTUP EVENT ---
@bot.event
async def on_ready():
    print(f'--- Bot Online: {bot.user} ---')
    print(f'Server ID: {GUILD_ID}')

# --- RUN ---
bot.run(os.getenv('DISCORD_TOKEN'))
