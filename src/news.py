from discord import app_commands
from discord.ext import commands
import requests
from bs4 import BeautifulSoup

class News(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="news", description="Zeigt die neuesten Fußballnachrichten an.")
    async def news(self, interaction):
        response = requests.get("https://www.fussballdaten.de/news/")
        soup = BeautifulSoup(response.content, "html.parser")
        
        news_items = soup.select("ul.timeline.news li.item a")[:5]

        news_message = ""
        for item in news_items:
            title = item.find("b").text
            link = f"<https://www.fussballdaten.de{item['href']}>"
            news_message += f"**{title}**\n{link}\n\n"
        
        await interaction.response.send_message(news_message)

async def setup(bot):
    await bot.add_cog(News(bot))
