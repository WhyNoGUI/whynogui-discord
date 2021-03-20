from collections import Mapping
from typing import Type

import discord
import discord.ext.commands as commands
import players
import games
import os
import random
import cards

with players.context() as player_ctx:
    games = []
    rps = ["r", "p", "s"]

    def getgame(player):
        return discord.utils.find(lambda g: player in g, games)


    class Status(commands.Cog):
        ranks = {
            "Beginner": 0,
            "Jackass Penguin": 200,
            "Little Penguin": 500,
            "Chinstrap Penguin": 1000,
            "Rockhopper Penguin": 5000,
            "Yellow-eyed Penguin": 10000,
            "Gentoo Penguin": 20000,
            "Snares-crested Penguin": 50000,
            "ERECT-crested Penguin": 100000,
            "Adelie Penguin": 200000,
            "Royal Penguin": 300000,
            "King Penguin": 400000,
            "Emperor Penguin": 500000,
            "Addicted Penguin": 1000000
        }

        def __init__(self):
            self.active_games: Mapping[str, games.AbstractGame] = {}

        @commands.command('show your coins')
        async def coins(self, ctx: commands.Context):
            author: discord.User = ctx.author
            #if author := ctx.author is not discord.User:
                #return
            await ctx.send(f"```@{author.display_name}, your current balance is {player_ctx.coins(str(author.id))}```")

        @commands.command('how your rank')
        async def rank(self, ctx: commands.Context):
            author: discord.User = ctx.author
            #if author := ctx.author is not discord.User:
                #return
            await ctx.send(f"```@{author.display_name}, your current rank is {player_ctx.rank(str(author.id))}```")

        @commands.command(help='show ranks and their costs')
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

        @commands.command(help='spend your coins to reach the next rank')
        async def rankup(self, ctx: commands.Context):
            author: discord.Member
            if author := ctx.author is not discord.Member:
                return
            if player_ctx.rank(str(author.id)) == "Addicted Penguin":
                await ctx.send("```Already reached the max rank!```")
                return
            if player_ctx.coins(str(author.id)) < self.ranks[self.ranks.index(player_ctx.rank(str(author.id))) + 1]:
                await ctx.send("```Not enough coins!```")
                return
            player_ctx.rank(list(self.ranks.keys())[self.ranks.index(player_ctx.rank(str(author.id))) + 1])

    class Casino(commands.Cog):
        _GAMES: Mapping[str, Type[games.AbstractGame]]

        def __init__(self):
            pass

        @commands.command(help='challenge user to rock-paper-scissors')
        async def new(self, ctx: commands.Context, amount: int):
            if not ctx.message.mentions:
                await ctx.send(f"```You didn't mention an opponent!```")
            p1: discord.User = ctx.author
            p2: discord.User = ctx.message.mentions[random.randint(0, len(ctx.message.mentions) - 1)]
            p1coins: int = player_ctx.coins(str(p1.id))
            p2coins: int = player_ctx.coins(str(p2.id))
            if p1coins < amount:
                await ctx.send(f"```You only have {p1coins} coins!```")
            elif p2coins < amount:
                await ctx.send(f"```{p2.display_name}, only has {p2coins} coins!```")
            elif p2 is None:
                await ctx.send(f"```Sorry, failed to find opponent!```")
            elif getgame(p1) is not None:
                await ctx.send("```Can not start a new game, you have to finish the current one first```")
            elif getgame(p2) is not None:
                await ctx.send(f"```{p2.display_name} is already in a game!```")
            else:
                games.append([p1, p2, amount])
                await ctx.send(f"```Game between {p1.display_name} and {p2.display_name} started.\n"
                               f"There are {amount} coins on the line```")

        @commands.command(help='pick your move for rock paper scissors (r/p/s)')
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

    bot = commands.Bot(command_prefix="bj!")
    bot.add_cog(Status())
    bot.add_cog(Casino())
    bot.run(os.environ["BOT_TOKEN"])

# @commands.command()
# async def game(self, ctx: commands.Context, action: str, game: str):
#     if game not in Casino._GAMES:
#         await ctx.send(f"Game {game} does not exist!")
#     elif action == 'start':
#         ...
#     elif action == 'info':
#         await ctx.send(Casino._GAMES[game].help())
#     else:
#         await ctx.send_help(self)
#     pass

