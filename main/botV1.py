import discord
import players
import os

client = discord.Client()

TOKEN = os.environ["TOKEN"]

@client.event
async def on_ready():
    print(f"{client.user} is now connected to the server {client.guilds[0]}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!coins"):
        playerid = int(message.content)
        with players.context() as ctx:
            balance = ctx.coins(str(playerid))
        await message.channel.send(f"{message.author}, your current balance is {balance}")

    if message.content.startswith("!coins"):
        playerid = int(message.content)
        with players.context() as ctx:
            rank = ctx.rank(str(playerid))
        await message.channel.send(f"{message.author}, your current rank is {rank}")


client.run(TOKEN)

