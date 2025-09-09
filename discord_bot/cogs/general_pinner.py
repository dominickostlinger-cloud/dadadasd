import discord
from discord.ext import commands, tasks

class GeneralPinner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_pins.start()

    @tasks.loop(count=1)
    async def update_pins(self):
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            # Find channels
            general_channel = discord.utils.get(guild.text_channels, name="general")
            rules_channel = discord.utils.get(guild.text_channels, name="┃📜┃rules")
            announcements_channel = discord.utils.get(guild.text_channels, name="┃📢┃announcements")

            # Prepare messages
            if general_channel:
                general_msg = (
                    "📌 Welcome to General! Please be respectful, follow the "
                    f"rules in <#{rules_channel.id if rules_channel else 'rules'}>, and have fun!"
                )
                await self._pin_or_update(general_channel, general_msg)

            if rules_channel:
                rules_msg = (
                    "📜 **Server Rules:**\n"
                    "1. Be respectful and kind.\n"
                    "2. No spam or self-promotion.\n"
                    "3. Never trust random DMs — **scammers are everywhere**.\n"
                    "4. Only click links from <#1411758261799227442>.\n"
                    "5. Keep conversations on-topic.\n\n"
                    "⚠️ Breaking these rules may result in warnings or bans."
                )
                await self._pin_or_update(rules_channel, rules_msg)

            if announcements_channel:
                ann_msg = (
                    "📢 **Announcements Channel**\n\n"
                    "All official updates, news, and important messages will be posted here.\n"
                    "👉 Make sure you have notifications enabled so you never miss an update!"
                )
                await self._pin_or_update(announcements_channel, ann_msg)

    async def _pin_or_update(self, channel, content):
        pinned_messages = await channel.pins()
        bot_pinned = None
        for msg in pinned_messages:
            if msg.author == self.bot.user:
                bot_pinned = msg
                break

        if bot_pinned:
            await bot_pinned.edit(content=content)
            print(f"✅ Updated pinned message in {channel.name}")
        else:
            msg = await channel.send(content)
            await msg.pin()
            print(f"✅ Sent and pinned new message in {channel.name}")

async def setup(bot):
    await bot.add_cog(GeneralPinner(bot))
