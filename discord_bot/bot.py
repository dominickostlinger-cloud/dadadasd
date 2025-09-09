import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PREFIX = os.getenv("COMMAND_PREFIX", "!")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.reactions = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)


async def load_all_cogs():
    cogs = [
        "cogs.welcome_pinned",
        "cogs.general_pinner",   # NEW cog
        "cogs.ai_responder"
    ]
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"✅ Loaded cog: {cog}")
        except Exception as e:
            print(f"❌ Failed to load cog {cog}: {e}")


@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


async def main():
    async with bot:
        await load_all_cogs()
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
