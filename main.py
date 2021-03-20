import discord
import discord.ext.commands as commands
import players
import os


with players.context() as player_ctx:
    class Status(commands.Cog):
        def __init__(self):
            pass

        @commands.command()
        async def coins(self, ctx: commands.Context):
            author: discord.Member
            if author := ctx.author is not discord.Member:
                return
            await ctx.send(f"{author.display_name}, your current balance is {player_ctx.coins(str(author.id))}")

        @commands.command()
        async def rank(self, ctx: commands.Context):
            author: discord.Member
            if author := ctx.author is not discord.Member:
                return
            await ctx.send(f"{author.display_name}, your current rank is {player_ctx.rank(str(author.id))}")

    class Casino(commands.Cog):
        def __init__(self):
            pass

        @commands.command()
        async def game(self, ctx: commands.Context):
            pass

    bot = commands.Bot(command_prefix="bj!")
    bot.add_cog(Status())
    bot.add_cog(Casino())
    bot.run(os.environ["BOT_TOKEN"])
