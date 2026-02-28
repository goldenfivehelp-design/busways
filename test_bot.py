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
class BuswaysTestBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # This syncs slash commands to your server so /test_sheet appears
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)
        print(f"Verified: Slash commands synced to {GUILD_ID}")

bot = BuswaysTestBot()

# --- 1. THE SLASH COMMAND (/test_sheet) ---
@bot.tree.command(name="test_sheet", description="Verifies Google Sheets connection")
@app_commands.checks.has_permissions(administrator=True)
async def test_sheet_slash(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row(["TEST", interaction.user.name, "Success", "Bot", now])
        cell = sheet.find("TEST")
        sheet.delete_rows(cell.row)
        await interaction.followup.send("✅ **Success!** Google Sheets is linked.")
    except Exception as e:
        await interaction.followup.send(f"❌ **Failed:** `{e}`")

# --- 2. THE PREFIX COMMAND (!sync) ---
# This fixes the "Command 'sync' is not found" error in your logs
@bot.command(name="sync")
async def manual_sync(ctx):
    await bot.tree.sync(guild=MY_GUILD)
    await ctx.send("🔄 **Sync Complete.** Try using `/test_sheet` now.")

# --- 3. THE PREFIX COMMAND (!test_sheet) ---
# This fixes the "Command 'test_sheet' is not found" error in your logs
@bot.command(name="test_sheet")
async def test_sheet_prefix(ctx):
    await ctx.send("⚠️ Please use the slash command version: `/test_sheet`")

bot.run(os.getenv('DISCORD_TOKEN'))
