import discord
from discord.ext import commands

class WelcomeGreeter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Try to get or create the welcome greeting channel
        guild = member.guild
        welcome_channel = discord.utils.get(guild.text_channels, name="┃👋┃greetings")
        if not welcome_channel:
            # Create the channel if it doesn't exist
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False)
            }
            welcome_channel = await guild.create_text_channel("┃👋┃greetings", overwrites=overwrites)
            print(f"✅ Created channel {welcome_channel.name}")

        # Send memecoin-friendly welcome message
        pinned_channel = discord.utils.get(guild.text_channels, name="┃📜┃welcome")
        pinned_link = f"<#{pinned_channel.id}>" if pinned_channel else "┃📜┃welcome"

        embed = discord.Embed(
            title=f"🚀 Welcome {member.display_name}!",
            description=(
                f"Yo memecoin enthusiast {member.mention}! Welcome to the MemeCoin Masterclass. 🎓\n\n"
                f"Make sure to **check the pinned message** in {pinned_link} to get started with everything you need!\n\n"
                "💎 Hold tight, learn, and may your coins moon! 🌙"
            ),
            color=discord.Color.purple()
        )

        await welcome_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(WelcomeGreeter(bot))
