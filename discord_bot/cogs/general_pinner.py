import discord
from discord.ext import commands, tasks
import os

# Messages from .env with defaults
DEFAULT_GENERAL_PIN = os.getenv(
    "GENERAL_PIN_MESSAGE",
    "📌 Welcome to <#1411758478158069801>! Please be respectful, read the rules here: <#1412529002886987878>"
)

DEFAULT_ANNOUNCEMENTS_PIN = os.getenv(
    "ANNOUNCEMENTS_PIN_MESSAGE",
    "📢 Welcome to #announcements! Keep an eye here for server news and updates."
)

DEFAULT_RULES_PIN = os.getenv(
    "RULES_PIN_MESSAGE",
    "⚠️ **Server Rules:**\n"
    "1️⃣ Never trust anyone who DMs you claiming to be staff or offering tokens.\n"
    "2️⃣ Only use links from the <#1411758261799227442> channel.\n"
    "3️⃣ Be respectful to everyone.\n"
    "4️⃣ Read pinned guides and follow instructions.\n\n"
    "Stay safe and enjoy the server! 🚀"
)


class GeneralPinner(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.pin_messages.start()

    @tasks.loop(count=1)
    async def pin_messages(self):
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            for ch in guild.text_channels:
                try:
                    lname = ch.name.lower()
                    if "general" in lname:
                        await self._ensure_pin(ch, DEFAULT_GENERAL_PIN)
                    elif "announcement" in lname:
                        await self._ensure_pin(ch, DEFAULT_ANNOUNCEMENTS_PIN)
                    elif "rules" in lname:
                        await self._ensure_pin(ch, DEFAULT_RULES_PIN)
                except Exception as e:
                    print(f"[general_pinner] Failed in #{ch.name} ({guild.name}): {e}")

    async def _ensure_pin(self, channel: discord.TextChannel, content: str):
        """Send or update a single pinned message by the bot in the given channel."""
        pins = await channel.pins()
        existing_by_bot = None
        for p in pins:
            if p.author == self.bot.user:
                existing_by_bot = p
                break

        if existing_by_bot:
            if existing_by_bot.content != content:
                await existing_by_bot.edit(content=content)
                print(f"[general_pinner] Updated pin in #{channel.name}")
        else:
            msg = await channel.send(content)
            try:
                await msg.pin()
                print(f"[general_pinner] Pinned message in #{channel.name}")
            except discord.Forbidden:
                print(f"[general_pinner] Missing permission to pin in #{channel.name}")

    @commands.command(name="pin_all")
    @commands.has_permissions(manage_messages=True)
    async def pin_all_cmd(self, ctx: commands.Context):
        """Manually trigger pinning in all general, announcements, and rules channels."""
        await self.pin_messages()
        await ctx.reply("✅ Checked and updated pins in all general, announcements, and rules channels.")


async def setup(bot: commands.Bot):
    await bot.add_cog(GeneralPinner(bot))
