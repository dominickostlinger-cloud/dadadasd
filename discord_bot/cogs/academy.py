import discord
from discord.ext import commands, tasks
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

SERVER_SOLANA_WALLET = os.getenv("SERVER_SOLANA_WALLET")
ACADEMY_ROLE = "Premium Member"
SOLANA_API_URL = "https://api.mainnet-beta.solana.com"
PAYMENT_AMOUNT_SOL = 1  # Required payment

# Track pending payments
pending_users = {}  # {user_id: {"wallet": "user_wallet", "paid": False}}
processed_signatures = set()

class Academy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.setup_channels.start()
        self.check_payments.start()

    # --------------------------
    # 1️⃣ Setup category and channels
    # --------------------------
    @tasks.loop(count=1)
    async def setup_channels(self):
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            # Create or get category
            category = discord.utils.get(guild.categories, name="┃🎓┃academy")
            if not category:
                category = await guild.create_category("┃🎓┃academy")
                print(f"✅ Created category {category.name}")

            # Create command channel
            cmd_channel = discord.utils.get(guild.text_channels, name="┃🎓┃academy-commands")
            if not cmd_channel:
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }
                cmd_channel = await guild.create_text_channel(
                    "┃🎓┃academy-commands", overwrites=overwrites, category=category
                )
                print(f"✅ Created channel {cmd_channel.name}")

            # Create info channel
            info_channel = discord.utils.get(guild.text_channels, name="┃🎓┃academy-info")
            if not info_channel:
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False)
                }
                info_channel = await guild.create_text_channel(
                    "┃🎓┃academy-info", overwrites=overwrites, category=category
                )
                print(f"✅ Created channel {info_channel.name}")

            # --------------------------
            # Pinned info embed
            # --------------------------
            embed = discord.Embed(
                title="🎓 Welcome to the MemeCoin Academy!",
                description=(
                    f"**How to join:**\n"
                    f"1️⃣ Send **{PAYMENT_AMOUNT_SOL} SOL** to the server wallet:\n"
                    f"`{SERVER_SOLANA_WALLET}`\n"
                    f"2️⃣ Use the command `!join_academy <your_wallet>` in {cmd_channel.mention}\n"
                    f"3️⃣ Check your payment status with `!payment_status`\n\n"
                    "Once your payment is confirmed, you will get the **Premium Member** role.\n\n"
                    "💡 Only use commands in the commands channel."
                ),
                color=discord.Color.green()
            )
            embed.set_footer(text="Pinned by the bot — do not remove this message.")

            pinned = await info_channel.pins()
            bot_pinned = None
            for msg in pinned:
                if msg.author == self.bot.user:
                    bot_pinned = msg
                    break

            if bot_pinned:
                await bot_pinned.edit(embed=embed)
                print(f"✅ Updated pinned embed in {info_channel.name}")
            else:
                msg = await info_channel.send(embed=embed)
                await msg.pin()
                print(f"✅ Sent and pinned embed in {info_channel.name}")

    # --------------------------
    # 2️⃣ User commands
    # --------------------------
    @commands.command()
    async def join_academy(self, ctx, user_wallet: str):
        """Register your wallet to join Academy"""
        if ctx.channel.name != "┃🎓┃academy-commands":
            return  # Ignore commands outside the command channel

        if ctx.author.id in pending_users:
            await ctx.send("❗ You already have a pending payment. Please wait for confirmation.")
            return

        pending_users[ctx.author.id] = {"wallet": user_wallet, "paid": False}

        embed = discord.Embed(
            title="🎓 Join the Academy",
            description=(
                f"Send **{PAYMENT_AMOUNT_SOL} SOL** to the server wallet below from your wallet:\n\n"
                f"`{SERVER_SOLANA_WALLET}`\n\n"
                "After sending, your role will be automatically assigned!"
            ),
            color=discord.Color.green()
        )
        embed.set_footer(text="Payments usually confirm within 30–60 seconds.")
        await ctx.send(embed=embed)

    @commands.command()
    async def payment_status(self, ctx):
        """Check if the user has completed payment"""
        if ctx.channel.name != "┃🎓┃academy-commands":
            return

        if ctx.author.id not in pending_users:
            await ctx.send("❌ You have no pending payment. Use `!join_academy <your_wallet>` first.")
            return

        if pending_users[ctx.author.id]["paid"]:
            await ctx.send("✅ Payment received! You already have Premium Academy access.")
        else:
            await ctx.send("⏳ Payment not yet confirmed. Please wait a moment.")

    # --------------------------
    # 3️⃣ Check payments loop
    # --------------------------
    @tasks.loop(seconds=30)
    async def check_payments(self):
        if not pending_users:
            return

        async with aiohttp.ClientSession() as session:
            try:
                for user_id, info in pending_users.items():
                    if info["paid"]:
                        continue

                    user_wallet = info["wallet"]

                    # Get last 10 signatures
                    payload = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getSignaturesForAddress",
                        "params": [user_wallet, {"limit": 10}]
                    }
                    async with session.post(SOLANA_API_URL, json=payload) as resp:
                        data = await resp.json()
                        txs = data.get("result", [])

                        for tx in txs:
                            sig = tx.get("signature")
                            if sig in processed_signatures:
                                continue

                            # Fetch transaction details
                            details_payload = {
                                "jsonrpc": "2.0",
                                "id": 1,
                                "method": "getTransaction",
                                "params": [sig, {"encoding": "jsonParsed"}]
                            }
                            async with session.post(SOLANA_API_URL, json=details_payload) as dresp:
                                ddata = await dresp.json()
                                txd = ddata.get("result")
                                if not txd:
                                    continue

                                try:
                                    pre_bal = txd["meta"]["preBalances"]
                                    post_bal = txd["meta"]["postBalances"]
                                    accounts = txd["transaction"]["message"]["accountKeys"]
                                    idx = [a["pubkey"] for a in accounts].index(SERVER_SOLANA_WALLET)
                                    diff = (post_bal[idx] - pre_bal[idx]) / 1_000_000_000

                                    if diff >= PAYMENT_AMOUNT_SOL:
                                        for guild in self.bot.guilds:
                                            member = guild.get_member(user_id)
                                            role = discord.utils.get(guild.roles, name=ACADEMY_ROLE)
                                            if member and role:
                                                await member.add_roles(role)
                                                try:
                                                    await member.send(
                                                        f"🎉 Payment of {diff} SOL received! You now have **{ACADEMY_ROLE}** access."
                                                    )
                                                except:
                                                    pass
                                                pending_users[user_id]["paid"] = True
                                                processed_signatures.add(sig)
                                                print(f"✅ Assigned role to {member} for tx {sig}")
                                                break
                                except Exception as e:
                                    print("Error parsing tx:", e)
            except Exception as e:
                print("Error checking Solana payments:", e)

    @setup_channels.before_loop
    @check_payments.before_loop
    async def before_loops(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Academy(bot))
