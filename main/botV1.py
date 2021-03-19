import discord
import players
<<<<<<< HEAD

client = discord.Client()

TOKEN = "ODIxMDIyNjMwMTk5MDMzODY3.YE9q6A.CIcehyB9UKwLvxJydcH1nEplUJ0"

=======
import os

client = discord.Client()

TOKEN = os.environ["TOKEN"]
>>>>>>> origin/main

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

