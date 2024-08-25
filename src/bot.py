import os
import discord
from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def setup_hook():
    await bot.load_extension('tabelle')
    await bot.load_extension('statistiken')
    await bot.load_extension('teilnehmer')
    await bot.load_extension('spielplan')
    await bot.tree.sync()

bot.setup_hook = setup_hook

@bot.event
async def on_ready():
    print(f'{bot.user} ist bereit!')

bot.run(TOKEN)
