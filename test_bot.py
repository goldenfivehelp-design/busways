import discord
from discord import app_commands
from discord.ext import commands
import os

# Your specific IDs
MY_GUILD = discord.Object(id=1418141167547187312)
APP_ID = 1476833993671446628 

class BuswaysBot(commands.Bot):
    def __init__(self):
        # Intents must be enabled in the Dev Portal!
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, application_id=APP_ID)

    async def setup_hook(self):
        # This force-pushes the /test_sheet command to your server menu
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)
        print(f"✅ SUCCESS: Slash commands pushed to Server {MY_GUILD.id}")

bot = BuswaysBot()

@bot.tree.command(name="test_sheet", description="Verifies the bot can see slash commands")
async def test_sheet(interaction: discord.Interaction):
    # This is the response that proves the slash command works
    await interaction.response.send_message("🚀 **Slash commands are now active!**", ephemeral=True)

# Prefix command as a backup
@bot.command()
async def sync(ctx):
    await bot.tree.sync(guild=MY_GUILD)
    await ctx.send("🔄 Manual sync triggered.")

bot.run(os.getenv('DISCORD_TOKEN'))
