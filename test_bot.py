import discord
import gspread
import os
import json
import requests
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIG ---
GUILD_ID = 1418141167547187312 
MY_GUILD = discord.Object(id=GUILD_ID)
APP_ID = "1476833993671446628" # Get this from Discord Dev Portal

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
        # 1. Manual API Registration (The way you showed me)
        url = f"https://discord.com/api/v10/applications/{APP_ID}/guilds/{GUILD_ID}/commands"
        headers = {"Authorization": f"Bot {os.getenv('DISCORD_TOKEN')}"}
        
        test_command_json = {
            "name": "test_sheet",
            "type": 1,
            "description": "Verifies Google Sheets connection"
        }
        
        # This pushes the command directly to Discord's servers
        r = requests.post(url, headers=headers, json=test_command_json)
        print(f"API Registration Status: {r.status_code}")

        # 2. Internal Library Sync
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)
        print("Internal Tree Synced.")

bot = BuswaysTestBot()

# --- THE SLASH COMMAND HANDLER ---
@bot.tree.command(name="test_sheet", description="Verifies Google Sheets connection")
@app_commands.checks.has_permissions(administrator=True)
async def test_sheet(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Log to Sheet
        sheet.append_row(["TEST", interaction.user.name, "Success", "System", now])
        # Find and Delete
        cell = sheet.find("TEST")
        sheet.delete_rows(cell.row)
        
        await interaction.followup.send("✅ **Success!** Google Sheets and Slash Commands are working.")
    except Exception as e:
        await interaction.followup.send(f"❌ **Failed:** `{e}`")

# --- PREFIX COMMANDS (To stop 'Command Not Found' errors) ---
@bot.command(name="sync")
async def sync_cmd(ctx):
    await bot.tree.sync(guild=MY_GUILD)
    await ctx.send("🔄 Synced.")

@bot.command(name="test_sheet")
async def test_prefix(ctx):
    await ctx.send("⚠️ Use the Slash Command: `/test_sheet`")

bot.run(os.getenv('DISCORD_TOKEN'))
