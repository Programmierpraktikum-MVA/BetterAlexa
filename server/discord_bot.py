import discord
from discord.ext import commands

import os
from dotenv import load_dotenv

import requests


"""
This function starts the discord bot named "BetterAlexa" and 
implements an command for forwarding a zoom invitation link.
"""
def start_discord_bot():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix="?", intents=intents)


    # Dein Bot-Token aus den .env variablen auslesen
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")

    # Variable, in der der Link gespeichert wird
    zoom_link = None

    @bot.event
    async def on_ready():
        print(f'Bot ist eingeloggt als {bot.user}')

    # Command zum Speichern des Zoom-Links
    @bot.command(name="join_zoom")
    async def join_zoom(ctx, link: str):
        global zoom_link
        zoom_link = link

        # Senden des Zoom links an die fast api
        url = "http://localhost:8006/handle_zoom_link"  # maybe needs to be adjusted 
        response = requests.post(url, json={"link": zoom_link})

        await ctx.send("Bot tritt dem Zoom-Meeting bei...")

    # Bot starten
    bot.run(TOKEN)