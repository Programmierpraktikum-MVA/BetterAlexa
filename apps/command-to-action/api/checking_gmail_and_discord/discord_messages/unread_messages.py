import discord
import asyncio
#working progress but i have to little time
token = "MTEyODMyNjkzODgzNTAyNjA1MQ.GPeCf9.TGql6x3e5By8pZLKUYRaTwAv1y6mIhoVQDyYtE"  # Replace with your Discord token

async def retrieve_unread_messages():
    intents = discord.Intents.default()
    intents.typing = False
    intents.presences = False

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'Logged in as {client.user.name} ({client.user.id})')

        # Retrieve unread messages from guild text channels
        for guild in client.guilds:
            for channel in guild.text_channels:
                await process_channel(channel)

        # Retrieve unread messages from private chats
        for channel in client.private_channels:
            await process_channel(channel)

        await client.close()

    async def process_channel(channel):
        unread_messages = []
        async for message in channel.history(limit=None, oldest_first=True):
            if message.author == client.user:
                break

            if not message.read:
                unread_messages.append(message.content)

        if unread_messages:
            print(f'Unread messages in channel {channel.name}:')
            for msg in unread_messages:
                print(f'- {msg}')
            print()

    await client.start(token)
    await asyncio.sleep(10)  # Adjust the duration as needed

asyncio.run(retrieve_unread_messages())
