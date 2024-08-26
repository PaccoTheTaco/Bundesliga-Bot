import discord
from discord.ext import commands
from discord import app_commands
import requests
from bs4 import BeautifulSoup

class Spieler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def replace_umlauts(self, text):
        replacements = {
            'ä': 'a',
            'ö': 'o',
            'ü': 'u',
            'ß': 's',
            'Ä': 'A',
            'Ö': 'O',
            'Ü': 'U'
        }
        for umlaut, replacement in replacements.items():
            text = text.replace(umlaut, replacement)
        return text

    def get_player_data(self, player_name):
        base_url = "https://www.bundesliga.com/de/bundesliga/spieler/"
        player_name_converted = self.replace_umlauts(player_name)
        player_url = base_url + player_name_converted.replace(" ", "-").lower()

        response = requests.get(player_url)
        if response.status_code != 200:
            return None, f"Fehler: Spieler '{player_name}' konnte nicht gefunden werden."

        soup = BeautifulSoup(response.text, 'html.parser')

        try:
            club = position = nationality = "Nicht verfügbar"
            info_divs = soup.find_all('div', class_='info')
            for info in info_divs:
                label = info.find('span', class_='label').text.strip()
                value = info.find('span', class_='value').text.strip()

                if label == "Club":
                    club = value
                elif label == "Position":
                    position = value
                elif label == "Nationalität":
                    nationality = value

            stats = {
                'Einsätze': 'Nicht verfügbar',
                'Laufdistanz (km)': 'Nicht verfügbar',
                'Begangene Fouls': 'Nicht verfügbar',
                'Gelbe Karten': 'Nicht verfügbar',
                'Tore': 'Nicht verfügbar',
                'Eigentore': 'Nicht verfügbar'
            }

            teamplay_section = soup.find('div', class_='section-teamplay')
            if teamplay_section:
                for row in teamplay_section.find_all('div', class_='row'):
                    key = row.find('div', class_='col col-8 key').text.strip()
                    value = row.find('div', class_='col col-4 value').text.strip()
                    if key in stats:
                        stats[key] = value

            discipline_section = soup.find('div', class_='section-discipline')
            if discipline_section:
                for row in discipline_section.find_all('div', class_='row'):
                    key = row.find('div', class_='col col-8 key').text.strip()
                    value = row.find('div', class_='col col-4 value').text.strip()
                    if key in stats:
                        stats[key] = value

            goalkeeping_section = soup.find('div', class_='section-goalkeeping')
            if goalkeeping_section:
                for row in goalkeeping_section.find_all('div', class_='row'):
                    key = row.find('div', class_='col col-8 key').text.strip()
                    value = row.find('div', class_='col col-4 value').text.strip()
                    if key in stats:
                        stats[key] = value

            career_stats_section = soup.find('section', class_='careerstats')
            if career_stats_section:
                for row in career_stats_section.find_all('div', class_='row'):
                    key = row.find('div', class_='col col-8 key').text.strip()
                    value = row.find('div', class_='col col-4 value').text.strip()
                    if key == "Tore":
                        stats['Tore'] = value

            player_data = {
                "name": player_name,
                "club": club,
                "position": position,
                "nationality": nationality,
                "stats": stats
            }
            return player_data, None

        except Exception as e:
            return None, f"Fehler bei der Verarbeitung der Daten: {str(e)}"

    @app_commands.command(name='spieler', description="Zeigt Informationen über einen Bundesliga-Spieler an.")
    async def spieler(self, interaction: discord.Interaction, player_name: str):
        player_data, error = self.get_player_data(player_name)

        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return

        stats = player_data["stats"]

        embed = discord.Embed(title=f"Informationen zu {player_data['name']}", color=0x1E90FF)
        embed.add_field(name="Club", value=player_data['club'], inline=True)
        embed.add_field(name="Position", value=player_data['position'], inline=True)
        embed.add_field(name="Nationalität", value=player_data['nationality'], inline=True)
        embed.add_field(name="Einsätze", value=stats['Einsätze'], inline=True)
        embed.add_field(name="Laufdistanz", value=f"{stats['Laufdistanz (km)']} km", inline=True)
        embed.add_field(name="Begangene Fouls", value=stats['Begangene Fouls'], inline=True)
        embed.add_field(name="Gelbe Karten", value=stats['Gelbe Karten'], inline=True)
        embed.add_field(name="Tore", value=stats['Tore'], inline=True)
        embed.add_field(name="Eigentore", value=stats['Eigentore'], inline=True)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    if not bot.get_cog('Spieler'):
        await bot.add_cog(Spieler(bot))
