import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import aiohttp
import urllib.parse

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
STEAM_APP_ID = 730  

if not TOKEN:
    raise ValueError("DISCORD_TOKEN not found in .env file")

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

async def get_steam_price(item_name: str):
    encoded_item = urllib.parse.quote(item_name)
    url = (
        f"https://steamcommunity.com/market/priceoverview/"
        f"?appid={STEAM_APP_ID}&currency=1&market_hash_name={encoded_item}"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()

    if data.get("success"):
        return data
    return None

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command(name="price")
async def price_check(ctx, *, item_name: str):
    """Fetch a Steam Market price."""
    channel = bot.get_channel(CHANNEL_ID)

    await channel.send(f"Fetching price for {item_name}...")

    data = await get_steam_price(item_name)
    if not data:
        await channel.send("Could not fetch price data. Check the item name or try again later.")
        return

    lowest_price = data.get("lowest_price", "N/A")
    median_price = data.get("median_price", "N/A")
    volume = data.get("volume", "N/A")

    embed = discord.Embed(
        title=f"Steam Market Price: {item_name}",
        color=discord.Color.green()
    )
    embed.add_field(name="Lowest Price", value=lowest_price, inline=True)
    embed.add_field(name="Median Price", value=median_price, inline=True)
    embed.add_field(name="Volume (24h)", value=volume, inline=False)
    embed.set_footer(text="Data from Steam Community Market")

    await channel.send(embed=embed)

bot.run(TOKEN)
