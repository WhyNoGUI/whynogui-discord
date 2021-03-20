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

        @commands.command()
        async def help(self, ctx: commands.Context):
            author: discord.Member
            if author := ctx.author is not discord.Member:
                return
            await ctx.send(f"""```bj!help:          bot commands
                                bj!coins:           show your coins
                                bj!rank:            show your rank
                                bj!ranks:           show ranks and their costs
                                bj!rankup:          spend your coins to reach the next rank
                                bj!new {{user}}:    challenge user to rock paper scissors
                                bj!play r/p/s:      pick your move for rock paper scissors```""")

        @commands.command()
        async def ranks(self, ctx: commands.Context):
            author: discord.Member
            if author := ctx.author is not discord.Member:
                return
            await ctx.send(f"""```Beginner              0
                                Jackass Penguin         200
                                Little Penguin          500
                                Chinstrap Penguin       1000
                                Rockhopper Penguin      5000
                                Yellow-eyed Penguin     10000
                                Gentoo Penguin          20000
                                Snares-crested Penguin  50000
                                ERECT-crested Penguin   100000
                                Adelie Penguin          200000
                                Royal Penguin           300000
                                King Penguin            400000
                                Emperor Penguin         500000
                                Addicted Penguin        1000000```""")

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
