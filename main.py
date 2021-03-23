import collections.abc
from typing import Type, Tuple, Optional, List, Any, Dict

import discord
import discord.ext.commands as commands
import players
import games
import os
import random
import cards

with players.context() as player_ctx:
    class Status(commands.Cog):

        def __init__(self):
            self.active_games: collections.Mapping[str, games.AbstractGame] = {}
            self.ranks = {
                "Beginner": 0,
                "Jackass Penguin": 200,
                "Little Penguin": 500,
                "Chinstrap Penguin": 1000,
                "Rockhopper Penguin": 5000,
                "Yellow-eyed Penguin": 10000,
                "Gentoo Penguin": 20000,
                "Snares-cres Penguin": 50000,
                "ERECT-crest Penguin": 100000,
                "Adelie Penguin": 200000,
                "Royal Penguin": 300000,
                "King Penguin": 400000,
                "Emperor Penguin": 500000,
                "Addicted Penguin": 1000000
            }

        @commands.command(help='show your profile')
        async def profile(self, ctx: commands.Context) -> None:
            author: discord.User = ctx.author
            embed = discord.Embed(title=author.display_name)
            embed.set_thumbnail(url=author.avatar_url)
            attributes = player_ctx.randc(str(author.id))
            embed.add_field(name="Rank:", value=attributes[0])
            embed.add_field(name="Balance:", value=str(attributes[1]) + " :moneybag:")
            await ctx.send(embed=embed)

        @commands.command(help='show all available ranks and their costs')
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

        @commands.command(help='spend coins to reach the next rank')
        async def rankup(self, ctx: commands.Context):
            author: discord.Member = ctx.author
            current_rank = player_ctx.rank(str(author.id))
            rank_names = list(self.ranks.keys())
            rank_costs = list(self.ranks.values())
            if current_rank == "Addicted Penguin":
                await ctx.send(embed=_embed_message("Already reached the max rank!"))
                return
            new_index = rank_names.index(current_rank) + 1
            if player_ctx.coins(str(author.id)) < rank_costs[new_index]:
                await ctx.send(embed=_embed_message("Not enough coins!"))
                return
            player_ctx.setrank(str(author.id), rank_names[new_index])
            player_ctx.addCoins(str(author.id), -rank_costs[new_index])
            await ctx.send(embed=_embed_message(f"{author.mention} Congratulations your new rank is "
                                                f"\"{player_ctx.rank(str(author.id))}\"!"))


    def _rps_emoji(symbol: str) -> str:
        if symbol == "r":
            return "https://cdn.discordapp.com/attachments/821013410657075211/823673429684125746/" \
                   "wdjDVCWJVk0MQAAAABJRU5ErkJggg.png"
        elif symbol == "p":
            return "https://cdn.discordapp.com/attachments/821013410657075211/823673669460033577/" \
                   "AfqQyt7KRUfZwAAAABJRU5ErkJggg.png"
        elif symbol == "s":
            return "https://cdn.discordapp.com/attachments/821013410657075211/823673548127862805/" \
                   "w8Rr5YIhg2tfgAAAABJRU5ErkJggg.png"


    def _check(author):
        def inner_check(message):
            return message.author == author

        return inner_check

    def _embed_message(message: str):
        return discord.Embed(description=message)


    class RPS(commands.Cog):
        _GAMES: collections.Mapping[str, Type[games.AbstractGame]]
        _RPS = ["r", "p", "s"]

        def __init__(self):
            self._active_games = []
            self._game_offers = []

        def _get_game(self, player: discord.User):  # -> Optional[List[Any]]:
            return discord.utils.find(lambda g: player in g, self._active_games)

        def _get_game_offer(self, player: discord.User):
            return discord.utils.find(lambda go: player in go, self._game_offers)

        @commands.command(help='challenge user to rock-paper-scissors')
        async def new(self, ctx: commands.Context, amount: int):
            if amount is None:
                embed = discord.Embed(description="Please specify the amount of  :coin:  you want to play for!")
                await ctx.send(embed=embed)
                return
            if ctx.message.mention_everyone:
                mentions = ctx.guild.members
                print("everyone")
            else:
                roles = ctx.message.role_mentions
                channels = ctx.message.channel_mentions
                mentions: set = ctx.message.mentions
                for role in roles:
                    mentions += role.members
                for channel in channels:
                    mentions += channel.members
            print(mentions)
            if mentions is None:
                await ctx.send(embed=_embed_message("You didn't mention an opponent!"))
                return
            p1: discord.User = ctx.author
            if len(mentions) == 1:
                p2: discord.User = mentions[0]
                p2coins: int = player_ctx.coins(str(p2.id))
                if p2coins < amount:
                    embed = discord.Embed(description=f"{p2.display_name} only has {p2coins}  :coin:")
                    await ctx.send(embed=embed)
                    return
            else:
                # candidats = [m for m in mentions if player_ctx.coins(str(m.id)) >= amount]
                for m in mentions:
                    print(player_ctx.coins(str(m.id)))
                filter(lambda men: player_ctx.coins(str(men.id)) >= amount, mentions)
                print(mentions)
                if mentions is None:
                    await ctx.send(embed=_embed_message("There is no one in this group who has enough  :coin:"))
                    return
                else:
                    p2: discord.User = mentions[random.randint(0, len(mentions) - 1)]

            p1coins: int = player_ctx.coins(str(p1.id))
            if p2 is None:
                await ctx.send(embed=_embed_message("Sorry, failed to find opponent!"))
            elif p1coins < amount:
                await ctx.send(embed=_embed_message(f"You only have {p1coins}  :coin:"))
            elif self._get_game(p1) is not None:
                await ctx.send(embed=_embed_message("You have to finish your current game before starting a new one!"))
            elif self._get_game(p2) is not None:
                await ctx.send(embed=_embed_message(f"{p2.display_name} is already in a game!"))
            else:
                self._game_offers.append([p1, p2, amount])
                await ctx.send(embed=_embed_message(f"{p2.mention}\n {p1.display_name} challenges you to a game of\n"
                                                    f"Rock, Paper, Scissors!\n[bj!accept/bj!decline]"))

        @commands.command()
        async def accept(self, ctx: commands.Context):
            author: discord.User = ctx.author
            if not self._get_game(author) is None:
                await ctx.send(embed=_embed_message("You have to finish your current game before starting a new one."))
            else:
                offered = discord.utils.find(lambda g: author in g, self._game_offers)
                if offered is None:
                    await ctx.send(embed=_embed_message("There is no offer for you to accept."))
                else:
                    self._active_games.append(offered)
                    self._game_offers.remove(offered)
                    await ctx.send(embed=_embed_message(f"Game between {author.display_name} and {offered[0].name} "
                                                        f"started.\nThere are {offered[2]} coins on the line!"))

        @commands.command()
        async def decline(self, ctx: commands.Context):
            author: discord.User = ctx.author
            offered = discord.utils.find(lambda g: author in g, self._game_offers)
            if offered is None:
                await ctx.send(embed=_embed_message("There is no offer for you to decline."))
            else:
                self._game_offers.remove(offered)
                await ctx.send(embed=_embed_message(f"{offered[0].mention} {author.display_name} declined your offer."))

        @commands.command(help='pick your move for rock paper scissors (r/p/s)')
        async def play(self, ctx: commands.Context, symbol: str):
            author: discord.User = ctx.author
            game = self._get_game(author)
            if game is None:
                await ctx.send(embed=_embed_message("You aren't currently in a a game!"))
            else:
                await ctx.message.delete()
            if len(game) == 5:
                other = RPS._RPS.index(game[3])
                current = RPS._RPS.index(symbol)
                embed = discord.Embed(title=author.display_name, description="\""+player_ctx.rank(str(author.id))+"\"")
                embed.set_thumbnail(url=author.avatar_url)
                embed.set_image(url=_rps_emoji(symbol))
                await ctx.send(embed=game[4])
                await ctx.send(embed=embed)
                if (other + 1) % 3 == current:
                    player_ctx.addCoins(str(game[0].id), -game[2])
                    player_ctx.addCoins(str(author.id), game[2])
                    await ctx.send(embed=_embed_message(f"{author.display_name} has won {game[2]} :coin:"))
                    # win_message = discord.Embed(description=player_ctx.win_message(str(author.id)))
                    # win_message.set_thumbnail(author.avatar_url)
                    # await ctx.send(win_message)
                elif (other - 1) % 3 == current:
                    player_ctx.addCoins(str(author.id), -game[2])
                    player_ctx.addCoins(str(game[0].id), game[2])
                    await ctx.send(embed=_embed_message(f"{game[0].display_name} has won {game[2]} :coin:"))
                    # win_message = discord.Embed(description=player_ctx.win_message(str(game[0].id)))
                    # win_message.set_thumbnail(game[0].avatar_url)
                    # await ctx.send(win_message)
                else:
                    await ctx.send(embed=_embed_message("It's a draw :handshake:"))
                self._active_games.remove(game)
            else:
                embed = discord.Embed(title=author.display_name, description="\""+player_ctx.rank(str(author.id))+"\"")
                embed.set_thumbnail(url=author.avatar_url)
                embed.set_image(url=_rps_emoji(symbol))
                game.append(symbol)
                game.append(embed)
                await ctx.send(embed=_embed_message(f"{author.display_name} has made a move"))

        @commands.command(help='cancel your current outgoing game challenge')
        async def cancel(self, ctx: commands.Context) -> None:
            author: discord.User = ctx.author
            game = self._get_game_offer(author)
            if game is None:
                await ctx.send(embed=_embed_message("You aren't currently in a game."))
                return
            self._game_offers.remove(game)
            await ctx.send(embed=_embed_message("Successfully canceled your game challenge!"))

    class Blackjack(commands.Cog):
        def __init__(self):
            pass

        async def bj(self, ctx: commands.Context):
            author: discord.User = ctx.author

    bot = commands.Bot(command_prefix="rps!")
    bot.add_cog(Status())
    bot.add_cog(RPS())
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
