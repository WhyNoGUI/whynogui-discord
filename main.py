import collections.abc
from typing import Type, Tuple, Optional, List, Any

import discord
import discord.ext.commands as commands
import players
import games
import os
import random

with players.context() as player_ctx:
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
            self.active_games: collections.Mapping[str, games.AbstractGame] = {}

        @commands.command(help='show your coins')
        async def coins(self, ctx: commands.Context):
            author: discord.User = ctx.author

            embed = discord.Embed(title = author.display_name)
            embed.add_field(name="Balance:", value=str(player_ctx.coins(str(author.id))))
            await ctx.send(embed=embed)

        @commands.command(help='how your rank')
        async def rank(self, ctx: commands.Context):
            author: discord.User = ctx.author

            embed = discord.Embed(title=author.display_name)
            embed.add_field(name="Rank:", value=str(player_ctx.rank(str(author.id))))
            await ctx.send(embed=embed)

        @commands.command(help='show ranks and their costs')
        async def ranks(self, ctx: commands.Context):
            author: discord.Member
            description = """```
                             Beginner                      0
                             Jackass Penguin             200
                             Little Penguin              500
                             Chinstrap Penguin          1000
                             Rockhopper Penguin         5000
                             Yellow-eyed Penguin       10000
                             Gentoo Penguin            20000
                             Snares-crested Penguin    50000
                             ERECT-crested Penguin    100000
                             Adelie Penguin           200000
                             Royal Penguin            300000
                             King Penguin             400000
                             Emperor Penguin          500000
                             Addicted Penguin        1000000```"""
            embed = discord.Embed(title="Ranks:", description=description)
            await ctx.send(embed=embed)

        @commands.command(help='spend your coins to reach the next rank')
        async def rankup(self, ctx: commands.Context):
            author: discord.Member = ctx.author
            if player_ctx.rank(str(author.id)) == "Addicted Penguin":
                await ctx.send("```Already reached the max rank!```")
                return
            if player_ctx.coins(str(author.id)) < self.ranks[self.ranks.index(player_ctx.rank(str(author.id))) + 1]:
                await ctx.send("```Not enough coins!```")
                return
            player_ctx.rank(list(self.ranks.keys())[self.ranks.index(player_ctx.rank(str(author.id))) + 1])


    class Casino(commands.Cog):
        _GAMES: collections.Mapping[str, Type[games.AbstractGame]]
        _RPS = ["r", "p", "s"]

        def __init__(self):
            self._active_games = []
            self._game_offers = []

        def _get_game(self, player: discord.User) -> Optional[List[Any]]:
            return discord.utils.find(lambda g: player in g, games)

        def _check(self, author):
            def inner_check(message):
                return message.author == author

            return inner_check

        @commands.command(help='challenge user to rock-paper-scissors')
        async def new(self, ctx: commands.Context, amount: int):
            if not ctx.message.mentions:
                await ctx.send(f"```You didn't mention an opponent!```")
                return
            p1: discord.User = ctx.author
            p2: discord.User = ctx.message.mentions[random.randint(0, len(ctx.message.mentions) - 1)]
            p1coins: int = player_ctx.coins(str(p1.id))
            p2coins: int = player_ctx.coins(str(p2.id))
            if p2 is None:
                await ctx.send(f"```Sorry, failed to find opponent!```")
            elif p1coins < amount:
                await ctx.send(f"```You only have {p1coins} coins!```")
            elif p2coins < amount:
                await ctx.send(f"```{p2.display_name} only has {p2coins} coins!```")
            elif self._get_game(p1) is not None:
                await ctx.send("```You have to finish your current game before starting a new one!```")
            elif self._get_game(p2) is not None:
                await ctx.send(f"```{p2.display_name} is already in a game!```")
            else:
                await ctx.send(f"{p2.mention()}, {p1.display_name} challenges you to a game of rock, paper, scissors\n"
                               f"[bj!accept/bj!decline]")
                # await ctx.bot.wait_for('message', check=self._check(ctx.author), timeout=30)
                self._game_offers.append([p1, p2, amount])
                # await ctx.send(f"```Game between {p1.display_name} and {p2.display_name} started.\n"
                # f"There are {amount} coins on the line```")

        @commands.command()
        async def accept(self, ctx: commands.Context):
            author: discord.User = ctx.author
            if not self._get_game(author) is None:
                await ctx.send("```You have to finish your current game before starting a new one.```")
            else:
                offered = discord.utils.find(lambda g: author in g, self._game_offers)
                if offered is None:
                    await ctx.send("```There is no offer for you to accept.```")
                else:
                    self._active_games.append(offered)
                    self._game_offers.remove(offered)
                    await ctx.send(f"```Game between {author.display_name} and {offered[0].name} started.\n"
                                   f"There are {offered[2]} coins on the line!```")

        @commands.command()
        async def decline(self, ctx: commands.Context):
            author: discord.User = ctx.author
            offered = discord.utils.find(lambda g: author in g, self._game_offers)
            if offered is None:
                await ctx.send("```There is no offer for you to decline.```")
            else:
                self._game_offers.remove(offered)
                await ctx.send(f"```{offered[0].mention()} {author.display_name} declined your offer.```")

        @commands.command(help='pick your move for rock paper scissors (r/p/s)')
        async def play(self, ctx: commands.Context, symbol: str):
            author: discord.User = ctx.author
            game = self._get_game(author)
            if game is None:
                await ctx.send("```You aren't currently in a a game!```")
            else:
                await ctx.message.delete()
            if len(game) == 4:
                other = Casino._RPS.index(game[3])
                current = Casino._RPS.index(symbol)
                if (other + 1) % 3 == current:
                    player_ctx.addCoins(str(game[0].id), -game[2])
                    player_ctx.addCoins(str(author.id), game[2])
                    await ctx.send(f"```{author.display_name} has won {game[2]} coins!```")
                elif (other - 1) % 3 == current:
                    player_ctx.addCoins(str(author.id), -game[2])
                    player_ctx.addCoins(str(game[0].id), game[2])
                    await ctx.send(f"```{game[0].display_name} has won {game[2]} coins!```")
                else:
                    await ctx.send("```It's a draw!```")
                self._active_games.remove(game)
            else:
                game.append(symbol)
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
