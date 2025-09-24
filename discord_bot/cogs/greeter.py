import os
import discord
from discord.ext import commands

class Greeter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.autorole_name = os.getenv("AUTOROLE_NAME", "Member")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild

        # Greeting channel
        channel = discord.utils.get(guild.text_channels, name="┃👋┃greetings")
        if channel:
            embed = discord.Embed(
                title="👋 Welcome!",
                description=(
                    f"Hey {member.mention}, welcome to **{guild.name}**! 🎉\n\n"
                    "We’re excited to have you here. Make sure to:\n"
                    "📖 Read the rules in <#1412529002886987878>\n"
                    "🎓 Explore the Academy in <#1412544163282554890>\n"
                    "🗺️ Check our roadmap in <#1411758192563851295>\n"
                    "🚀 Let’s build together and take memecoins to the moon!"
                ),
                color=discord.Color.blurple()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(embed=embed)

        # Auto-role assignment
        role = discord.utils.get(guild.roles, name=self.autorole_name)
        if role:
            try:
                await member.add_roles(role)
                print(f"✅ Gave {member} the role {role.name}")
            except discord.Forbidden:
                print(f"⚠️ Missing permission to assign role {role.name}")
        else:
            print(f"⚠️ Role '{self.autorole_name}' not found in {guild.name}")

async def setup(bot):
    await bot.add_cog(Greeter(bot))
