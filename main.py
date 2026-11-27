import os, discord
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError: pass
from lit import lit, take_quota
TOKEN = os.environ["DISCORD_BOT_TOKEN"]
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

@tree.command(name="ping", description="Check whether the bot is online")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong 🏓 online")

@tree.command(name="lit", description="Cited multi-model PubMed summary (3/day)")
@discord.app_commands.describe(target="Target or drug, e.g. KRAS G12C")
async def lit_cmd(interaction: discord.Interaction, target: str):
    if not take_quota(interaction.user.id):
        return await interaction.response.send_message("Daily limit reached (3 /lit per day). Try again tomorrow.", ephemeral=True)
    await interaction.response.defer(thinking=True)
    try: txt = await lit(target[:100])
    except Exception as e: txt = f"Sorry, /lit failed ({type(e).__name__})."
    await interaction.followup.send(txt, allowed_mentions=discord.AllowedMentions.none())

@client.event
async def on_ready():
    for g in client.guilds:
        tree.copy_global_to(guild=g)
        await tree.sync(guild=g)
    print("READY", client.user, [g.name for g in client.guilds], flush=True)

client.run(TOKEN)
