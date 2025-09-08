import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("❌ DISCORD_TOKEN is missing in .env!")

# -------------------
# Intents
# -------------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------
# Cog loader
# -------------------
async def load_all_cogs():
    cogs = [
        "cogs.welcome",
        "cogs.welcome_pinned",
        "cogs.academy",
        "cogs.ai_responder",
        "cogs.support"
    ]
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"✅ Loaded cog: {cog}")
        except Exception as e:
            print(f"❌ Failed to load cog {cog}: {e}")

# -------------------
# Test command
# -------------------
@bot.command()
async def test(ctx):
    await ctx.send("✅ Commands are working!")

# -------------------
# On ready
# -------------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} | Connected to {len(bot.guilds)} guild(s)")

# -------------------
# Run bot
# -------------------
async def main():
    await load_all_cogs()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
