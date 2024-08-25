import discord
from discord.ext import commands
from discord.ui import Button, View
import requests
from bs4 import BeautifulSoup

BUNDESLIGA_URL = "https://www.bundesliga.com/de/bundesliga/tabelle"

def get_table_data():
    response = requests.get(BUNDESLIGA_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    table_rows = soup.select('tbody tr')
    table = []
    for row in table_rows:
        position = row.select_one('.rank span').text.strip()
        team_name = row.select_one('.team div').text.strip()
        points = row.select_one('.pts span').text.strip()
        matches_played = row.select_one('.matches span').text.strip()
        table.append({
            "position": position,
            "team_name": team_name,
            "points": points,
            "matches_played": matches_played
        })
    return table

def create_embed(start_index=0):
    table_data = get_table_data()
    embed = discord.Embed(title="Bundesliga Tabelle", color=discord.Color.blue())
    end_index = start_index + 6
    for team in table_data[start_index:end_index]:
        embed.add_field(
            name=f"{team['position']}. {team['team_name']}",
            value=f"Punkte: {team['points']}, Spiele: {team['matches_played']}",
            inline=False
        )
    
    total_pages = len(table_data) // 6 + (1 if len(table_data) % 6 != 0 else 0)
    current_page = start_index // 6 + 1
    embed.set_footer(text=f"Seite {current_page} von {total_pages}")
    
    return embed

class TableView(View):
    def __init__(self):
        super().__init__()
        self.current_index = 0

    @discord.ui.button(label="Zurück", style=discord.ButtonStyle.primary)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_index > 0:
            self.current_index -= 6
            embed = create_embed(self.current_index)
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Weiter", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_index + 6 < len(get_table_data()):
            self.current_index += 6
            embed = create_embed(self.current_index)
            await interaction.response.edit_message(embed=embed, view=self)

class Tabelle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} ist bereit!')

    @discord.app_commands.command(name="tabelle", description="Zeigt die aktuelle Bundesliga Tabelle an.")
    async def tabelle(self, interaction: discord.Interaction):
        embed = create_embed(0)
        view = TableView()
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Tabelle(bot))
