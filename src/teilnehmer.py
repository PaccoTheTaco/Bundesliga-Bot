import discord
from discord.ext import commands
from discord.ui import Button, View
import requests
from bs4 import BeautifulSoup

BUNDESLIGA_URL = "https://www.bundesliga.com/de/bundesliga/tabelle"

def get_all_teams():
    response = requests.get(BUNDESLIGA_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    table_rows = soup.select('tbody tr')
    teams = []
    for row in table_rows:
        abbreviation = row.select_one('.team div span.d-inline-block').text.strip()
        full_name = row.select_one('.team div span.d-none.d-sm-inline-block').text.strip()
        teams.append({
            "full_name": full_name,
            "abbreviation": abbreviation
        })
    return teams

def create_teams_embed(teams, start_index=0):
    embed = discord.Embed(title="Teilnehmende Vereine der Bundesliga", color=discord.Color.blue())
    end_index = min(start_index + 6, len(teams))
    for team in teams[start_index:end_index]:
        embed.add_field(
            name=f"{team['full_name']}",
            value=f"Abkürzung: {team['abbreviation']}",
            inline=False
        )
    embed.set_footer(text=f"Seite {start_index // 6 + 1} von {(len(teams) + 5) // 6}")
    return embed

class TeamsView(View):
    def __init__(self, teams):
        super().__init__()
        self.teams = teams
        self.current_index = 0
        self.update_buttons()

    def update_buttons(self):
        total_teams = len(self.teams)
        self.children[0].disabled = self.current_index == 0
        self.children[1].disabled = self.current_index + 6 >= total_teams

    @discord.ui.button(label="Zurück", style=discord.ButtonStyle.primary, disabled=True)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_index > 0:
            self.current_index -= 6
            embed = create_teams_embed(self.teams, self.current_index)
            self.update_buttons()
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Weiter", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_index + 6 < len(self.teams):
            self.current_index += 6
            embed = create_teams_embed(self.teams, self.current_index)
            self.update_buttons()
            await interaction.response.edit_message(embed=embed, view=self)

class Teilnehmer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} ist bereit!')

    @discord.app_commands.command(name="teilnehmer", description="Zeigt alle teilnehmenden Vereine der Bundesliga mit ihren Abkürzungen an.")
    async def teilnehmer(self, interaction: discord.Interaction):
        teams = get_all_teams()
        if teams:
            embed = create_teams_embed(teams)
            view = TeamsView(teams)
            await interaction.response.send_message(embed=embed, view=view)
        else:
            await interaction.response.send_message("Keine Vereine gefunden.")

async def setup(bot):
    await bot.add_cog(Teilnehmer(bot))
