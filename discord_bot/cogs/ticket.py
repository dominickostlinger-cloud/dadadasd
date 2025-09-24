import discord
from discord.ext import commands
import asyncio

# -------------------------
# Close Ticket View
# -------------------------
class CloseTicketView(discord.ui.View):
    def __init__(self, channel_id: int):
        super().__init__(timeout=None)
        self.channel_id = channel_id

    @discord.ui.button(label="❌ Close Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket_button")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            return await interaction.response.send_message("❌ This ticket no longer exists.", ephemeral=True)

        # Only staff can close tickets
        staff_role = discord.utils.get(interaction.guild.roles, name="Staff")
        if staff_role not in interaction.user.roles and not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message("❌ Only staff can close this ticket.", ephemeral=True)

        await channel.delete(reason="Ticket closed")

# -------------------------
# Ticket Creation View
# -------------------------
class TicketView(discord.ui.View):
    user_locks = {}  # prevent duplicate ticket creation

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Support", style=discord.ButtonStyle.primary, custom_id="support_ticket_btn")
    async def support_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._create_ticket(interaction, "Support")

    @discord.ui.button(label="🎓 Join Academy", style=discord.ButtonStyle.success, custom_id="academy_ticket_btn")
    async def academy_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._create_ticket(interaction, "Academy")

    @discord.ui.button(label="📢 Social Media Coins", style=discord.ButtonStyle.secondary, custom_id="social_ticket_btn")
    async def social_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._create_ticket(interaction, "Social Media Coins")

    @discord.ui.button(label="💼 Commercial Offers", style=discord.ButtonStyle.danger, custom_id="commercial_ticket_btn")
    async def commercial_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._create_ticket(interaction, "Commercial Offers")

    async def _create_ticket(self, interaction: discord.Interaction, kind: str):
        user_id = interaction.user.id

        # --- Prevent multiple tickets opening at the same time ---
        if TicketView.user_locks.get(user_id, False):
            return await interaction.response.send_message("⚠️ Please wait, your ticket is being created.", ephemeral=True)
        TicketView.user_locks[user_id] = True

        try:
            guild = interaction.guild

            # Ensure Staff role exists
            staff_role = discord.utils.get(guild.roles, name="Staff")
            if not staff_role:
                staff_role = await guild.create_role(
                    name="Staff",
                    permissions=discord.Permissions(manage_channels=True, manage_messages=True),
                    mentionable=False,
                    reason="Staff role needed for ticket system"
                )

            # Construct channel name with type and username
            safe_name = interaction.user.name.lower().replace(" ", "-")
            channel_name = f"{kind.lower()}-{safe_name}"

            # Prevent duplicate ticket channels
            existing = discord.utils.get(guild.text_channels, name=channel_name)
            if existing:
                return await interaction.response.send_message(f"❌ You already have a ticket: {existing.mention}", ephemeral=True)

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                staff_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }

            channel = await guild.create_text_channel(
                channel_name,
                overwrites=overwrites,
                reason=f"{kind} ticket for {interaction.user}"
            )

            await asyncio.sleep(0.5)  # ensure channel ready

            # Temporarily make Staff role mentionable for this message only
            await staff_role.edit(mentionable=True)
            staff_ping = staff_role.mention if staff_role else "@here"

            msg_text = (
                f"{interaction.user.mention} opened a **{kind} Ticket**.\n"
                f"{staff_ping}, please assist!\n\n"
                "Use the button below to close this ticket when done."
            )

            msg = await channel.send(msg_text, view=CloseTicketView(channel.id))
            await msg.pin()  # Pin the ticket message

            # Set role back to unmentionable after sending
            await staff_role.edit(mentionable=False)

            await interaction.response.send_message(f"✅ Your {kind} ticket has been created: {channel.mention}", ephemeral=True)

        finally:
            TicketView.user_locks[user_id] = False  # release lock

# -------------------------
# Cog
# -------------------------
class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ticket system loaded ✅")
        self.bot.add_view(TicketView())  # register persistent view

        # Ensure Staff role exists in all guilds
        for guild in self.bot.guilds:
            staff_role = discord.utils.get(guild.roles, name="Staff")
            if not staff_role:
                staff_role = await guild.create_role(
                    name="Staff",
                    permissions=discord.Permissions(manage_channels=True, manage_messages=True),
                    mentionable=False,
                    reason="Staff role needed for ticket system"
                )
                print(f"Created 'Staff' role in {guild.name}")

        # send the panel automatically in ┃🆘┃support・ticket
        channel_id = 1411759866804048044  # << replace with your channel ID
        channel = self.bot.get_channel(channel_id)
        if channel:
            embed = discord.Embed(
                title="🎟 SUPPORT TICKET",
                description=(
                    "Hey, I’m **Rix**, the owner of this community.\n"
                    "If you need help, want to join the Academy, discuss social media coins, "
                    "or have business offers — open a ticket below.\n\n"
                    "💰 **Academy Payments (SOL):**\n"
                    "Always open a ticket **before paying**.\n"
                    "Only send SOL to this address:\n"
                    "`6CMPvwc6uxjid7HSWsjj2GuKfw66obq9j8wbHZBCaP7P`\n\n"
                    "⚠️ Please don’t open tickets for unnecessary reasons.\n"
                    "Our staff team — and myself when needed — will assist you directly.\n\n"
                    "– **Rix (Owner)**"
                ),
                color=discord.Color.blue()
            )
            # Remove old panels to prevent duplicates
            async for msg in channel.history(limit=10):
                if msg.author == self.bot.user:
                    await msg.delete()
            await channel.send(embed=embed, view=TicketView())

# -------------------------
# Setup
# -------------------------
async def setup(bot):
    await bot.add_cog(Ticket(bot))
