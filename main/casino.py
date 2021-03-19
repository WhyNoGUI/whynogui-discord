import os
import discord
import players
from dotenv import load_dotenv

load_dotenv()

client = discord.Client()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")
con = players.context()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("bj!help"):
        return

    if message.content.startswith("bj!coins"):
        print("coins")
        await message.channel.send(message.author + ':' + con.coins("me"))

    if message.content == "bj!bj":
        await message.channel.send("test1")

    if message.content == "bj!hit":
        print('test')
        await message.channel.send("test2")

    if message.content == 'bj!roulette':
        return

    if message.content == 'bj!slots':
        return


client.run(TOKEN)
