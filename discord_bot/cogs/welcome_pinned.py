import discord
from discord.ext import commands, tasks

class WelcomePinned(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.send_welcome_once.start()

    @tasks.loop(count=1)
    async def send_welcome_once(self):
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            # Welcome channel
            welcome_channel = discord.utils.get(guild.text_channels, name="┃📜┃welcome")
            if not welcome_channel:
                print(f"Channel ┃📜┃welcome not found in {guild.name}")
                continue

            # Target channels
            support_channel = discord.utils.get(guild.text_channels, name="┃🆘┃support・ticket")
            roadmap_channel = discord.utils.get(guild.text_channels, name="┃🗺️┃roadmap")
            academy_channel = discord.utils.get(guild.text_channels, name="┃🎓┃academy-info")
            rules_channel = discord.utils.get(guild.text_channels, name="┃📜┃rules")
            announcements_channel = discord.utils.get(guild.text_channels, name="┃📢┃announcements")

            # Clickable links
            support_link = f"<#{support_channel.id}>" if support_channel else "┃🆘┃support・ticket"
            roadmap_link = f"<#{roadmap_channel.id}>" if roadmap_channel else "┃🗺️┃roadmap"
            academy_link = f"<#{academy_channel.id}>" if academy_channel else "┃🎓┃academy-info"
            rules_link = f"<#{rules_channel.id}>" if rules_channel else "┃📜┃rules"
            announcements_link = f"<#{announcements_channel.id}>" if announcements_channel else "┃📢┃announcements"

            # Embed
            embed = discord.Embed(
                title="🎓 Welcome to the MemeCoin Masterclass!",
                description=(
                    "Hello there! Welcome to our server dedicated to **memecoin mastery**.\n\n"
                    "This server is made for people who want to make **generational wealth** "
                    "and learn everything about launching and selling memecoins! "
                    "You can also learn how to **trade**, participate in **Alpha Signals** "
                    "and **Coin launches**!\n\n"
                    f"📜 **Read the rules first:** {rules_link}\n"
                    f"💬 **Need help or have questions?** {support_link}\n"
                    f"🗺️ **Check our roadmap and pinned guides:** {roadmap_link}\n"
                    f"🎓 **Join the Academy and learn more:** {academy_link}\n"
                    f"📢 **Official announcements:** {announcements_link}\n\n"
                    "Enjoy your stay and happy memecoins! 🚀"
                ),
                color=discord.Color.green()
            )
            embed.set_footer(text="Pinned by the bot — only one welcome message per server.")

            # Check if bot already pinned a message
            pinned_messages = await welcome_channel.pins()
            bot_pinned = None
            for msg in pinned_messages:
                if msg.author == self.bot.user:
                    bot_pinned = msg
                    break

            if bot_pinned:
                await bot_pinned.edit(embed=embed)
                print(f"✅ Updated pinned welcome message in {welcome_channel.name}")
            else:
                msg = await welcome_channel.send(embed=embed)
                await msg.pin()
                print(f"✅ Sent and pinned new welcome message in {welcome_channel.name}")

async def setup(bot):
    await bot.add_cog(WelcomePinned(bot))
