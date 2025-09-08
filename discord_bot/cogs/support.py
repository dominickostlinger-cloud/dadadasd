import discord
from discord.ext import commands

class Support(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ticket(self, ctx, *, reason=None):
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel = await ctx.guild.create_text_channel(f"ticket-{ctx.author.name}", overwrites=overwrites)
        await channel.send(f"Hello {ctx.author.mention}, a staff member will assist you soon. Reason: {reason}")

async def setup(bot):
    await bot.add_cog(Support(bot))
