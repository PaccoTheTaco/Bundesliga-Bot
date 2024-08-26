import requests
from bs4 import BeautifulSoup
import discord
from discord.ext import commands
from discord import app_commands

class TopSpieler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def scrape_top_players(self):
        url = "https://www.bundesliga.com/de/bundesliga/statistiken/spieler/tore"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        players = []
        player_cards = soup.find_all('stats-player-card', class_='linkActive')

        for card in player_cards:
            try:
                first_name = card.find('span', class_='first').text.strip()
                last_name = card.find('span', class_='last').text.strip()
                name = f"{first_name} {last_name}"

                player_link_tag = card.find_parent('a', href=True)
                player_link = "https://www.bundesliga.com" + player_link_tag['href'].split('#')[0] if player_link_tag else None

                club = self.get_club_from_player_page(player_link) if player_link else "Unbekannt"

                goals_span = card.find('span', class_='value')
                goals = goals_span.text.strip() if goals_span else "0"
                
                players.append({
                    "name": name,
                    "club": club,
                    "goals": goals
                })
            except AttributeError:
                continue
        
        return players

    def get_club_from_player_page(self, url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            club_tag = soup.find('div', class_='info col-12 col-md-6').find('a')
            club_name = club_tag.text.strip() if club_tag else "Unbekannt"
            return club_name
        except Exception:
            return "Unbekannt"

    def create_embed(self, players):
        embed = discord.Embed(title="Top Spieler der Bundesliga", color=discord.Color.blue())
        for player in players:
            embed.add_field(
                name=player['name'],
                value=f"Club: {player['club']}\nTore: {player['goals']}",
                inline=False
            )
        return embed

    @app_commands.command(name='topspieler', description="Zeigt die Top-Torschützen der Bundesliga")
    async def show_top_players(self, interaction: discord.Interaction):
        await interaction.response.defer()  

        players = self.scrape_top_players()
        if not players:
            await interaction.followup.send("Es konnten keine Spielerinformationen abgerufen werden.")
            return

        embed = self.create_embed(players)
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TopSpieler(bot))
