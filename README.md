# Discord Bundesliga Bot

English version below

Um den Bot auf deinen Server laufen zu lassen musst du folgende Schritte beachten:
- Python3 muss installiert sein (du kannst das mit "python3 --version" testen)
- wenn Python nicht installier ist musst du Python installieren mit sudo apt install python3
- ziehe nun den Ordner src auf deinen Server 
- installiere nun pip via "sudo apt install python3-pip"
- installiere nun über pip die benötigten Pakete mit "pip install discord.py python-dotenv requests beautifulsoup4"
- erstelle im Ordner src die Datei .env und füge da "DISCORD_TOKEN=dein_discord_bot_token" und "API_FOOTBALL_KEY=dein_football_api_key" ein und erstetze die Token mit deinen Token (Football API Token von https://www.api-football.com/sports Discord Token von https://discord.com/developers/applications)
- Navigiere nun in den src Ordner und führe Python3 bot.py aus und dann läuft der Bot 

------------------

English version:

To run the bot on your server you have to follow these steps:
- Python3 must be installed (you can test this with ‘python3 --version’)
- if Python is not installed you have to install Python with sudo apt install python3
- now drag the src folder to your server 
- now install pip via ‘sudo apt install python3-pip’
- now install the required packages via pip with ‘pip install discord.py python-dotenv requests beautifulsoup4’
- create the file .env in the src folder and add ‘DISCORD_TOKEN=your_discord_bot_token’ and ‘API_FOOTBALL_KEY=your_football_api_key’ and replace the tokens with your tokens (Football API Token from https://www.api-football.com/sports Discord Token from https://discord.com/developers/applications)
- Now navigate to the src folder and execute Python3 bot.py and then the bot will run 



