import os
import discord

# load dotenv
from dotenv import load_dotenv
load_dotenv(dotenv_path='../../.env')

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')

bot = discord.Client(intents=discord.Intents.all())

# bot successfully connected to discord
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# handling messages
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content == '!BetterAlexa':
        # join voice channel of message author
        if message.author.voice:
            await message.author.voice.channel.connect()

# leave voice channel if bot is the only member
@bot.event
async def on_voice_state_update(member, before, after):
    # check if bot is the only member in voice channel
    if before.channel is not None and len(before.channel.members) == 1 and before.channel.members[0].id == bot.user.id:
        await before.channel.disconnect()


bot.run(DISCORD_TOKEN)
