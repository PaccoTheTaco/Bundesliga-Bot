import discord
from discord.ext import commands
from discord import app_commands
import requests
from bs4 import BeautifulSoup

class Mannschaft(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vereine = [
            {"name": "fc-augsburg", "keywords": ["augsburg", "fca"]},
            {"name": "1-fc-union-berlin", "keywords": ["union", "fcu"]},
            {"name": "vfl-bochum-1848", "keywords": ["bochum", "boc"]},
            {"name": "sv-werder-bremen", "keywords": ["bremen", "svw"]},
            {"name": "fc-st-pauli", "keywords": ["st-pauli", "stp"]},
            {"name": "borussia-dortmund", "keywords": ["dortmund", "bvb"]},
            {"name": "eintracht-frankfurt", "keywords": ["frankfurt", "sge"]},
            {"name": "sc-freiburg", "keywords": ["freiburg", "scf"]},
            {"name": "1-fc-heidenheim-1846", "keywords": ["heidenheim", "fch"]},
            {"name": "tsg-hoffenheim", "keywords": ["hoffenheim", "tsg"]},
            {"name": "holstein-kiel", "keywords": ["kiel", "ksv"]},
            {"name": "rb-leipzig", "keywords": ["leipzig", "rbl"]},
            {"name": "bayer-04-leverkusen", "keywords": ["leverkusen", "b04"]},
            {"name": "1-fsv-mainz-05", "keywords": ["mainz", "m05"]},
            {"name": "borussia-moenchengladbach", "keywords": ["gladbach", "bmg"]},
            {"name": "fc-bayern-muenchen", "keywords": ["bayern", "fcb"]},
            {"name": "vfb-stuttgart", "keywords": ["stuttgart", "vfb"]},
            {"name": "vfl-wolfsburg", "keywords": ["wolfsburg", "wob"]},
        ]

    def get_team_url(self, team_key):
        for verein in self.vereine:
            if team_key in verein["keywords"]:
                return f"https://www.bundesliga.com/de/bundesliga/clubs/{verein['name']}"
        return None

    @app_commands.command(name='mannschaft', description="Zeigt Statistiken eines Bundesliga-Vereins an")
    async def fetch_team_stats(self, interaction: discord.Interaction, team: str):
        team_key = team.lower()
        url = self.get_team_url(team_key)
        
        if not url:
            await interaction.response.send_message("Verein oder Abkürzung nicht gefunden. Bitte überprüfe die Eingabe.")
            return

        response = requests.get(url)
        if response.status_code != 200:
            await interaction.response.send_message("Konnte die Daten nicht abrufen.")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        stadium = soup.find("span", class_="stadiumName").text.strip()

        stats = {}
        for stat in soup.find_all("div", class_="element"):
            key = stat.find("div", class_="key").text.strip()
            value = stat.find("div", class_="value").text.strip()
            stats[key] = value

        embed = discord.Embed(title=f"Statistiken für {team.title()}", color=0x1e90ff)
        embed.add_field(name="Stadion", value=stadium, inline=False)

        for stat_name in [
            "Ballbesitz (%)", "Karten", "Gelbe Karten", "Flanken aus dem Spiel", "Laufdistanz (km)",
            "Fouls am Gegner", "Tore", "Intensive Läufe", "Eigentore", "Passquote (%)", "Elfmeter",
            "Verwandelte Elfmeter", "Torschüsse", "Pfosten- oder Lattentreffer", "Sprints",
            "Gewonnene Kopfballduelle", "Gewonnene Zweikämpfe"
        ]:
            if stat_name in stats:
                embed.add_field(name=stat_name, value=stats[stat_name], inline=True)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Mannschaft(bot))
