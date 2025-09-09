import discord
from discord.ext import commands
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

class AIResponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        allowed_channels = ['general-chat', 'trading-chat']
        if message.channel.name in allowed_channels:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": message.content}]
                )
                await message.channel.send(response.choices[0].message['content'])
            except Exception as e:
                print("AI error:", e)

        # <-- MUST call this so commands still work
        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(AIResponder(bot))
