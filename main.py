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
TARGET_CHANNEL_ID = 1420690312531017850 
TARGET_MESSAGE_ID = 1476842017886572648 

# --- 2. THE BACKGROUND LOOP ---
@tasks.loop(minutes=1.0)
async def update_status_loop():
    try:
        channel = bot.get_channel(TARGET_CHANNEL_ID) or await bot.fetch_channel(TARGET_CHANNEL_ID)
        message = await channel.fetch_message(TARGET_MESSAGE_ID)
        
        API_KEY = os.getenv('STATUSPAGE_API_KEY')
        headers = {"Authorization": f"OAuth {API_KEY}"}
        
        def get_comp_status(comp_id, label):
            url = f"https://api.statuspage.io{PAGE_ID}/components/{comp_id}"
            try:
                r = requests.get(url, headers=headers, timeout=10)
                
                # --- CONSOLE DEBUG LOGGING ---
                if r.status_code == 200:
                    data = r.json()
                    raw_status = data.get('status', 'unknown')
                    # This prints "Opal Status: operational" to your Railway logs
                    print(f"DEBUG: {label} Status: {raw_status}") 

                    status_map = {
                        "operational": "✅ Operational",
                        "degraded_performance": "🟨 Degraded performance",
                        "partial_outage": "🟧 Partial outage",
                        "major_outage": "🟥 Major outage",
                        "under_maintenance": "🟦 Under maintenance"
                    }
                    return status_map.get(raw_status, f"❓ {raw_status.replace('_', ' ').title()}")
                else:
                    print(f"DEBUG ERROR: {label} failed with {r.status_code}: {r.text}")
                    return "❌ Connection Error"
            except Exception as e:
                print(f"DEBUG NETWORK ERROR: {label} - {e}")
                return "❌ Connection Error"

        # Fetch statuses with labels for the console
        opal_status = get_comp_status(OPAL_ID, "Opal")
        game_status = get_comp_status(GAME_ID, "Game")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create Embed
        embed = discord.Embed(
            title="Busways Status",
            description="Hello, I am Busways Assistance here to provide data of the status of the game.\nThis data is updated every minute.",
            color=5814783 
        )
        embed.add_field(name="Datastores", value=f"Opal Data Status: {opal_status}", inline=False)
        embed.add_field(name=f"Game Status: {game_status}", value=" ", inline=False)
        embed.set_footer(text=f"Updated {current_time} (Local Time)")

        await message.edit(embed=embed)
        print(f"Discord Message Updated: {current_time}")

    except Exception as e:
        print(f"Loop Error: {e}")

# --- 3. STARTUP ---
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    if not update_status_loop.is_running():
        update_status_loop.start()

bot.run(os.getenv('DISCORD_TOKEN'))
