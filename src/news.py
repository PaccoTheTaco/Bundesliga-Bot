from discord import app_commands
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import discord

class News(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="news", description="Zeigt die neuesten Fußballnachrichten an.")
    async def news(self, interaction):
        response = requests.get("https://www.fussballdaten.de/news/")
        soup = BeautifulSoup(response.content, "html.parser")
        
        news_items = soup.select("ul.timeline.news li.item a")[:5]

        embed = discord.Embed(
            title="Aktuelle Fußballnachrichten",
            description="Hier sind die neuesten Schlagzeilen:",
            color=discord.Color.blue()
        )

        for item in news_items:
            title = item.find("b").text
            link = f"https://www.fussballdaten.de{item['href']}"
            embed.add_field(name=title, value=f"[Mehr erfahren]({link})", inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(News(bot))
