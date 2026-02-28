import discord
import requests
import os
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
    # Statuspage API uses 'Authorization: OAuth <key>'
    headers = {"Authorization": f"OAuth {API_KEY}"}
    
    # Corrected API URL Structure
    url = f"https://api.statuspage.io/v1/pages/{PAGE_ID}/components/{comp_id}"
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            raw_status = data.get('status', 'unknown')
            print(f"DEBUG: {label} fetched as {raw_status}")
            
            status_map = {
                "operational": "✅ Operational",
                "degraded_performance": "🟨 Degraded performance",
                "partial_outage": "\U0001f7e7 Partial outage",
                "major_outage": "🟥 Major outage",
                "under_maintenance": "🟦 Under maintenance"
            }
            return status_map.get(raw_status, f"❓ {raw_status.replace('_', ' ').title()}")
        
        else:
            print(f"DEBUG ERROR: {label} API returned {r.status_code}: {r.text}")
            return "❌ API Error"
            
    except requests.exceptions.RequestException as e:
        print(f"DEBUG NETWORK ERROR: {label} - {e}")
        return "⚠️ Connection Failed"

# --- 3. THE BACKGROUND LOOP ---
@tasks.loop(minutes=1.0)
async def update_status_loop():
    try:
        # 1. Access Discord elements
        channel = bot.get_channel(TARGET_CHANNEL_ID) or await bot.fetch_channel(TARGET_CHANNEL_ID)
        message = await channel.fetch_message(TARGET_MESSAGE_ID)
        
        # 2. Fetch data from Statuspage
        opal_status = get_comp_status(OPAL_ID, "Opal")
        game_status = get_comp_status(GAME_ID, "Game")
        
        # 3. Build the Embed
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        embed = discord.Embed(
            title="Busways Status",
            description="Hello, I am Busways Assistance. I monitor game data and update this status every minute.",
            color=5814783 
        )
        
        embed.add_field(
            name="Datastores", 
            value=f"Opal Data Status: **{opal_status}**", 
            inline=False
        )
        embed.add_field(
            name="Game Connectivity", 
            value=f"Game Status: **{game_status}**", 
            inline=False
        )
        embed.set_footer(text=f"Last Sync: {current_time} (UTC/Server Time)")

        # 4. Update the message
        await message.edit(embed=embed)
        print(f"Update Successful: {current_time}")

    except discord.NotFound:
        print("Loop Error: Message or Channel not found. Check your IDs.")
    except Exception as e:
        print(f"Loop Error: {e}")

# --- 4. STARTUP ---
@bot.event
async def on_ready():
    print(f'--- Bot Online as {bot.user} ---')
    if not update_status_loop.is_running():
        update_status_loop.start()

# Start the bot
bot.run(os.getenv('DISCORD_TOKEN'))
