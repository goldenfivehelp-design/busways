import discord
import requests
import os
import time  # Used for Unix timestamps
from discord.ext import commands, tasks
from datetime import datetime

# --- 1. SETUP ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Configuration Constants
PAGE_ID = "pb7vnbyp9dky"
OPAL_ID = "lx84tk5jzmt5"
GAME_ID = "ktdfbtft0ffq"

# Discord IDs
TARGET_CHANNEL_ID = 1420690312531017850 
TARGET_MESSAGE_ID = 1476842017886572648 

# --- 2. HELPER FUNCTIONS ---
def get_comp_status(comp_id, label):
    """Fetches component status using the official Statuspage API v1 path."""
    API_KEY = os.getenv('STATUSPAGE_API_KEY')
    headers = {"Authorization": f"OAuth {API_KEY}"}
    
    # Corrected API URL Structure
    url = f"https://api.statuspage.io/v1/pages/{PAGE_ID}/components/{comp_id}"
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            raw_status = data.get('status', 'unknown')
            
            status_map = {
                "operational": "✅ Operational",
                "degraded_performance": "🟨 Degraded performance",
                "partial_outage": "🟧 Partial outage",
                "major_outage": "🟥 Major outage",
                "under_maintenance": "🟦 Under maintenance"
            }
            return status_map.get(raw_status, f"❓ {raw_status.replace('_', ' ').title()}")
        else:
            return "❌ API Error"
    except Exception as e:
        print(f"DEBUG NETWORK ERROR: {label} - {e}")
        return "⚠️ Connection Failed"

# --- 3. THE BACKGROUND LOOP ---
@tasks.loop(minutes=1.0)
async def update_status_loop():
    try:
        channel = bot.get_channel(TARGET_CHANNEL_ID) or await bot.fetch_channel(TARGET_CHANNEL_ID)
        message = await channel.fetch_message(TARGET_MESSAGE_ID)
        
        # Fetch actual statuses
        opal_status = get_comp_status(OPAL_ID, "Opal")
        game_status = get_comp_status(GAME_ID, "Game")
        
        # --- DYNAMIC TIME LOGIC ---
        # This gets the current Unix time (seconds since 1970)
        unix_timestamp = int(time.time())
        # Discord format: <t:timestamp:f> shows "Date at Time" in the USER's timezone
        discord_time_string = f"<t:{unix_timestamp}:f>"

        # Create Embed
        embed = discord.Embed(
            title="Busways Status",
            description=f"Hello, I am Busways Assistance. I provide live data on the status of our systems.\n**Last Sync:** {discord_time_string}",
            color=5814783 
        )
        
        embed.add_field(
            name="Datastores", 
            value=f"Opal Data Status: **{opal_status}**", 
            inline=False
        )
        
        embed.add_field(
            name="Game Status", 
            value=f"Current Status: **{game_status}**", 
            inline=False
        )
        
        # Using :R at the end shows a countdown like "1 minute ago"
        embed.set_footer(text="Updates every minute • Auto-adjusts to your timezone")

        await message.edit(embed=embed)
        print(f"Discord Message Updated: {datetime.now()}")

    except Exception as e:
        print(f"Loop Error: {e}")

# --- 4. STARTUP ---
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    if not update_status_loop.is_running():
        update_status_loop.start()

bot.run(os.getenv('DISCORD_TOKEN'))
