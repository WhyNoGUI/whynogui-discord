import discord
import discord.ext.commands as commands
import players
import os


with players.context() as player_ctx:
    bot = commands.Bot(command_prefix="bj!")

    @bot.event
    async def on_ready():
        print(f"{bot.user.display_name} is now connected to the server {bot.guilds[0]}")

    @bot.command()
    async def coins(ctx: commands.Context):
        author: discord.User = ctx.author
        await ctx.send(f"{author.display_name}, your current balance is {player_ctx.coins(str(author.id))}")

    @bot.command()
    async def rank(ctx: commands.Context):
        author: discord.User = ctx.author
        await ctx.send(f"{author.display_name}, your current rank is {player_ctx.rank(str(author.id))}")

    bot.run(os.environ["BOT_TOKEN"])
