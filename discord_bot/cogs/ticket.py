import discord
from discord.ext import commands

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # persistent view

    @discord.ui.button(label="Ask a Question", style=discord.ButtonStyle.primary, emoji="🎫")
    async def ask_question(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._create_ticket(interaction, "question")

    @discord.ui.button(label="Join the Academy", style=discord.ButtonStyle.success, emoji="🎓")
    async def join_academy(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._create_ticket(interaction, "academy")

    async def _create_ticket(self, interaction: discord.Interaction, kind: str):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        existing = discord.utils.get(guild.text_channels, name=f"ticket-{interaction.user.id}")
        if existing:
            return await interaction.response.send_message(
                f"You already have a ticket: {existing.mention}", ephemeral=True
            )

        channel = await guild.create_text_channel(
            f"ticket-{interaction.user.id}", overwrites=overwrites, reason=f"Ticket for {interaction.user}"
        )

        if kind == "question":
            msg_text = f"{interaction.user.mention} opened a **Question Ticket**.\nPlease describe your question and a staff member will assist you."
        else:
            msg_text = f"{interaction.user.mention} wants to **Join the Academy**.\nPlease wait for staff instructions."

        msg = await channel.send(msg_text, view=CloseTicketView(channel))
        await msg.pin()
        await interaction.response.send_message(f"✅ Your {kind} ticket has been created: {channel.mention}", ephemeral=True)


class CloseTicketView(discord.ui.View):
    def __init__(self, channel):
        super().__init__(timeout=None)  # persistent view
        self.channel = channel

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="❌")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message("❌ Only staff can close this ticket.", ephemeral=True)
        modal = CloseTicketConfirm(self.channel)
        await interaction.response.send_modal(modal)


class CloseTicketConfirm(discord.ui.Modal, title="Confirm Ticket Closure"):
    def __init__(self, channel):
        super().__init__()
        self.channel = channel

    reason = discord.ui.TextInput(
        label="Reason for closing the ticket (optional)",
        style=discord.TextStyle.short,
        required=False,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        await self.channel.delete()
        await interaction.response.send_message(
            f"✅ Ticket closed. Reason: {self.reason.value or 'No reason provided'}", ephemeral=True
        )


class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ticketpanel")
    @commands.has_permissions(manage_guild=True)
    async def ticket_panel(self, ctx):
        view = TicketView()
        await ctx.send("**Need help? Open a ticket using the buttons below.**", view=view)

    @commands.Cog.listener()
    async def on_ready(self):
        # register persistent views so buttons appear after bot restart
        self.bot.add_view(TicketView())


async def setup(bot):
    await bot.add_cog(Ticket(bot))
