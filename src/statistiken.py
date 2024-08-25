import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup

BUNDESLIGA_URL = "https://www.bundesliga.com/de/bundesliga/tabelle"

def get_team_stats(team_name_or_abbreviation):
    response = requests.get(BUNDESLIGA_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    table_rows = soup.select('tbody tr')

    for row in table_rows:
        full_name = row.select_one('.team div').text.strip()
        abbreviation = row.select_one('.team div span').text.strip()

        if team_name_or_abbreviation.lower() in [full_name.lower(), abbreviation.lower()]:
            games = row.select_one('.matches span').text.strip()
            wins = row.select_one('.wins span').text.strip()
            draws = row.select_one('.draws span').text.strip()
            losses = row.select_one('.losses span').text.strip()
            goals = row.select_one('.goals span').text.strip()
            goal_diff = row.select_one('.difference span').text.strip()
            points = row.select_one('.pts span').text.strip()

            goals_scored, goals_conceded = map(int, goals.split(':'))

            return {
                "team_name": full_name,
                "games": games,
                "wins": wins,
                "draws": draws,
                "losses": losses,
                "goals_scored": goals_scored,
                "goals_conceded": goals_conceded,
                "goal_diff": goal_diff,
                "points": points
            }

    return None

def create_stats_embed(stats):
    embed = discord.Embed(title=f"Statistiken für {stats['team_name']}", color=discord.Color.blue())
    embed.add_field(name="Spiele", value=stats['games'], inline=True)
    embed.add_field(name="Punkte", value=stats['points'], inline=True)
    embed.add_field(name="\u200B", value="\u200B", inline=True)
    embed.add_field(name="Siege", value=stats['wins'], inline=True)
    embed.add_field(name="Unentschieden", value=stats['draws'], inline=True)
    embed.add_field(name="Niederlagen", value=stats['losses'], inline=True)
    embed.add_field(name="Tore geschossen", value=stats['goals_scored'], inline=True)
    embed.add_field(name="Tore bekommen", value=stats['goals_conceded'], inline=True)
    embed.add_field(name="Tor-Differenz", value=stats['goal_diff'], inline=True)
    
    return embed

class Statistiken(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} ist bereit!')

    @discord.app_commands.command(name="statistiken", description="Zeigt die Statistiken eines Bundesliga-Vereins an.")
    @discord.app_commands.describe(team_name_or_abbreviation="Voller Name oder Abkürzung des Teams")
    async def statistiken(self, interaction: discord.Interaction, team_name_or_abbreviation: str):
        stats = get_team_stats(team_name_or_abbreviation)
        
        if stats:
            embed = create_stats_embed(stats)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"Verein '{team_name_or_abbreviation}' nicht gefunden. Bitte überprüfe den Namen oder die Abkürzung.")

async def setup(bot):
    await bot.add_cog(Statistiken(bot))
