import discord
from discord.ext import commands

class AdminTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reload(self, ctx, cog: str):
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            await ctx.send(f"🔄 Reloaded `{cog}` successfully.")
        except Exception as e:
            await ctx.send(f"⚠️ Failed to reload `{cog}`: {e}")

    @commands.command()
    async def listcogs(self, ctx):
        cogs = list(self.bot.cogs.keys())
        await ctx.send(f"📂 Loaded cogs: {', '.join(cogs)}")

async def setup(bot):
    await bot.add_cog(AdminTools(bot))
