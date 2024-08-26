import discord
from discord.ext import commands
from discord import app_commands
import requests
from bs4 import BeautifulSoup

class Spielplan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache = {}
        self.titles = {}
        self.verein_mapping = {
            "scf": "sc-freiburg",
            "bvb": "borussia-dortmund",
            "fcb": "fc-bayern-muenchen",
            "b04": "bayer-04-leverkusen",
            "tsg": "tsg-hoffenheim",
            "rbl": "rb-leipzig",
            "svw": "sv-werder-bremen",
            "fca": "fc-augsburg",
            "m05": "1-fsv-mainz-05",
            "fcu": "1-fc-union-berlin",
            "stp": "fc-st-pauli",
            "fch": "1-fc-heidenheim-1846",
            "bmg": "borussia-moenchengladbach",
            "wob": "vfl-wolfsburg",
            "ksv": "holstein-kiel",
            "boc": "vfl-bochum-1848",
            "vfb": "vfb-stuttgart",
            "sge": "eintracht-frankfurt"
        }

    @app_commands.command(name="spielplan", description="Zeigt den Spielplan für einen angegebenen Spieltag oder Verein an.")
    async def spielplan(self, interaction: discord.Interaction, spieltag: int = None, verein: str = None):
        if spieltag:
            url = f"https://www.bundesliga.com/de/bundesliga/spieltag/2024-2025/{spieltag}"
            is_verein = False
            title = f"Spieltag {spieltag}"
        elif verein:
            verein_key = verein.lower().replace(' ', '-')
            verein = self.verein_mapping.get(verein_key, verein_key)
            url = f"https://www.bundesliga.com/de/bundesliga/spieltag/2024-2025/{verein}"
            is_verein = True
            title = f"Spielplan {verein.capitalize()}"
        else:
            await interaction.response.send_message("Bitte gib entweder einen Spieltag oder einen Verein an.", ephemeral=True)
            return

        await interaction.response.defer()

        try:
            response = requests.get(url)
            if response.status_code == 404:
                await interaction.followup.send(f"Der Verein '{verein}' wurde nicht gefunden.", ephemeral=True)
                return

            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            spiele = self.extract_matches(soup)
            if spiele:
                pages = self.paginate(spiele, 6) if is_verein else self.paginate(spiele, 1)
                self.cache[interaction.user.id] = pages
                self.titles[interaction.user.id] = title
                embed = self.create_embed(pages, page=0, title=title)
                await interaction.followup.send(embed=embed, view=self.PaginationView(interaction.user.id, self))
            else:
                await interaction.followup.send("Konnte keine Spiele finden. Bitte versuche es später erneut.")
        except requests.exceptions.RequestException as e:
            await interaction.followup.send(f"Fehler beim Abrufen des Spielplans: {e}")

    def extract_matches(self, soup):
        matches_by_day = {}
        match_rows = soup.find_all('div', class_='matchRow')

        for row in match_rows:
            date_header = row.find_previous('span', class_='day')
            if date_header:
                date = date_header.get_text(strip=True)
                if date and not date[-1].isspace():
                    date = date.replace("Freitag", "Freitag ").replace("Samstag", "Samstag ").replace("Sonntag", "Sonntag ")
            else:
                date = "Unbekanntes Datum"

            time_header = row.find_previous('span', class_='time')
            time = time_header.get_text(strip=True) if time_header else "Unbekannte Zeit"

            teams = row.find_all('div', class_='name')
            home_team = teams[1].get_text(strip=True) if len(teams) >= 2 else "Unbekannt"
            away_team = teams[3].get_text(strip=True) if len(teams) >= 2 else "Unbekannt"

            match_info = f"**{time}**\n{home_team} - {away_team}"
            if date not in matches_by_day:
                matches_by_day[date] = []
            matches_by_day[date].append(match_info)

        return list(matches_by_day.items())

    def paginate(self, matches_by_day, page_size):
        pages = []
        for i in range(0, len(matches_by_day), page_size):
            pages.append(matches_by_day[i:i + page_size])
        return pages

    def create_embed(self, matches_by_day, page, title):
        embed = discord.Embed(title=title, color=0x00ff00)
        page_matches = matches_by_day[page]

        for date, matches in page_matches:
            match_list = "\n\n".join(matches)
            embed.add_field(name=date, value=match_list, inline=False)

        embed.set_footer(text=f"Seite {page + 1}/{len(matches_by_day)}")
        return embed

    class PaginationView(discord.ui.View):
        def __init__(self, user_id, cog):
            super().__init__(timeout=60)
            self.user_id = user_id
            self.cog = cog
            self.page = 0

        @discord.ui.button(label="Zurück", style=discord.ButtonStyle.primary, disabled=True)
        async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id == self.user_id:
                self.page -= 1
                if self.page == 0:
                    button.disabled = True
                self.children[1].disabled = False
                title = self.cog.titles.get(self.user_id, "Spielplan")
                embed = self.cog.create_embed(self.cog.cache[self.user_id], self.page, title)
                await interaction.response.edit_message(embed=embed, view=self)

        @discord.ui.button(label="Weiter", style=discord.ButtonStyle.primary)
        async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id == self.user_id:
                self.page += 1
                if self.page + 1 >= len(self.cog.cache[self.user_id]):
                    button.disabled = True
                self.children[0].disabled = False
                title = self.cog.titles.get(self.user_id, "Spielplan")
                embed = self.cog.create_embed(self.cog.cache[self.user_id], self.page, title)
                await interaction.response.edit_message(embed=embed, view=self)

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            return interaction.user.id == self.user_id

async def setup(bot):
    await bot.add_cog(Spielplan(bot))
