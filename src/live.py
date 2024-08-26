import discord
from discord.ext import commands
from discord import app_commands
import requests
import os

class Live(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv('API_FOOTBALL_KEY')

    @app_commands.command(name="live", description="Zeigt alle laufenden Bundesliga-Spiele an.")
    async def live_games(self, interaction: discord.Interaction):
        url = "https://v3.football.api-sports.io/fixtures"
        headers = {'x-apisports-key': self.api_key}
        params = {'league': '78', 'season': '2023', 'live': 'all'}

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if data['response']:
            embed = discord.Embed(title="Bundesliga Live-Spiele", color=discord.Color.green())
            for match in data['response']:
                teams = match['teams']
                score = match['goals']
                status = match['fixture']['status']['elapsed']
                embed.add_field(
                    name=f"{teams['home']['name']} vs {teams['away']['name']}",
                    value=f"Stand: {score['home']} - {score['away']} (Minute: {status})",
                    inline=False
                )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Derzeit gibt es keine laufenden Bundesliga-Spiele.")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync()

async def setup(bot):
    await bot.add_cog(Live(bot))
