import discord
import discord.ext.commands as commands
import players
import os
import random


with players.context() as player_ctx:
    games = []
    rps = ["r", "p", "s"]

    def getgame(player):
        return discord.utils.find(lambda g: player in g, games)


    class Status(commands.Cog):
        def __init__(self):
            pass

        @commands.command()
        async def coins(self, ctx: commands.Context):
            author: discord.User = ctx.author
            #if author := ctx.author is not discord.User:
                #return
            await ctx.send(f"```{author.display_name}, your current balance is {player_ctx.coins(str(author.id))}```")

        @commands.command()
        async def rank(self, ctx: commands.Context):
            author: discord.User = ctx.author
            #if author := ctx.author is not discord.User:
                #return
            await ctx.send(f"```{author.display_name}, your current rank is {player_ctx.rank(str(author.id))}```")

        @commands.command()
        async def new(self, ctx: commands.Context, amount: int):
            author: discord.User = ctx.author
            p2 = ctx.message.mentions[random.randint(0, len(ctx.message.mentions) - 1)]
            p1coins = player_ctx.coins(str(author.id))
            if p1coins < amount:
                await ctx.send(f"```{author.display_name}, you only have {p1coins} coins```")
                return
            p2coins = player_ctx.coins(str(p2.id))
            if p2coins < amount:
                await ctx.send(f"```{p2.display_name}, you only have {p2coins} coins```")
                return
            if p2 is None:
                await ctx.send(f"```Sorry, can't find player {ctx.message.split(' ')[1]}```")
                return
            if getgame(author) is None and getgame(p2) is None:
                games.append([author, p2, amount])
                await ctx.send(f"```Game between {author.display_name} and {p2.name} started.\nThere are {amount} coins on the line```")
            else:
                await ctx.send("```Can not start a new game, you have to finish the current one first```")

        @commands.command()
        async def play(self, ctx: commands.Context, symbol: str):
            author: discord.User = ctx.author
            game = getgame(author)
            if len(game) == 4:
                other = rps.index(game[3])
                current = rps.index(symbol)
                if (other + 1) % 3 == current:
                    player_ctx.addCoins(str(game[0].id), -game[2])
                    player_ctx.addCoins(str(author.id), game[2])
                    await ctx.send(f"```{author} has won```")
                elif (other - 1) % 3 == current:
                    player_ctx.addCoins(str(author.id), -game[2])
                    player_ctx.addCoins(str(game[0].id), game[2])
                    await ctx.send(f"```{game[0]} has won {game[2]} coins!```")
                else:
                    await ctx.send("```It's a draw!```")
                games.remove(game)
            else:
                game.append(symbol)
                await ctx.message.delete()
                await ctx.send(f"```{author.display_name} has made a move```")

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
