import collections.abc
from typing import Type, Tuple, Optional, List, Any, Dict

import discord
import discord.ext.commands as commands
from discord import colour

import players
import games
import os
import random
import cards

with players.context() as player_ctx:

    class RPSMove:
        def __init__(self, player=None, symbol: str = None):
            self.player = player
            self.symbol = symbol
            pass

    class RPSGame:
        def __init__(self, channel=None, player1: discord.User = None, player2: discord.User = None, coins: int = 0,
                     move1: RPSMove = None, move2: RPSMove = None,
                     embed1: discord.Embed = None, embed2: discord.Embed = None):
            self.channel = channel
            self.player1 = player1
            self.player2 = player2
            self.coins = coins
            self.move1 = move1
            self.move2 = move2
            self.embed1 = embed1
            self.embed2 = embed2
            pass

        def _contains_player(self, player) -> bool:
            return self.player1 == player or self.player2 == player

    class Status(commands.Cog):

        def __init__(self):
            self.active_games: collections.Mapping[str, games.AbstractGame] = {}
            self.ranks = {
                "Baby Penguin": [0, "https://cdn.discordapp.com/attachments/824289443787046942/824402816985989120/unknown.png"],
                "Dwarf Penguin": [200, "https://cdn.discordapp.com/attachments/824289443787046942/824401769052241940/unknown.png"],
                "Jackass Penguin": [500, "https://cdn.discordapp.com/attachments/824289443787046942/824402331004960798/unknown.png"],
                "Chinstrap Penguin": [1000, "https://cdn.discordapp.com/attachments/824289443787046942/824403013618761738/unknown.png"],
                "Rockhopper Penguin": [5000, "https://cdn.discordapp.com/attachments/824289443787046942/824403296810172426/unknown.png"],
                "Yellow-eyed Penguin": [10000, "https://cdn.discordapp.com/attachments/824289443787046942/824402072002756608/unknown.png"],
                "Gentoo Penguin": [20000, "https://cdn.discordapp.com/attachments/824289443787046942/824403640939970600/unknown.png"],
                # varchar(20) isn't enough for some names
                "Snares-cres Penguin": [50000, "https://cdn.discordapp.com/attachments/824289443787046942/824404344655970304/unknown.png"],
                "ERECT-crest Penguin": [100000, "https://cdn.discordapp.com/attachments/824289443787046942/824404591859990618/unknown.png"],
                "Adelie Penguin": [200000, "https://cdn.discordapp.com/attachments/824289443787046942/824405326282883092/unknown.png"],
                "Royal Penguin": [300000, "https://cdn.discordapp.com/attachments/824289443787046942/824400915888996412/unknown.png"],
                "King Penguin": [400000, "https://cdn.discordapp.com/attachments/824289443787046942/824401123812966412/unknown.png"],
                "Emperor Penguin": [500000, "https://cdn.discordapp.com/attachments/824289443787046942/824400356413931551/unknown.png"],
                "Addicted Penguin": [1000000, "https://cdn.discordapp.com/attachments/824289443787046942/824406373852774422/unknown.png"]
            }

        @commands.command(help='show your profile')
        async def profile(self, ctx: commands.Context) -> None:
            author: discord.User = ctx.author
            embed = discord.Embed(title=author.display_name)
            embed.set_thumbnail(url=author.avatar_url)
            attributes = player_ctx.randc(str(author.id))
            embed.add_field(name="Rank:", value=attributes[0])
            embed.add_field(name="Balance:", value=str(attributes[1]) + " :moneybag:")
            embed.set_image(url=self.ranks[attributes[0]][1])
            await ctx.send(embed=embed)

        @commands.command(help='show all available ranks and their costs')
        async def ranks(self, ctx: commands.Context):
            author: discord.Member
            description = """```
                             Baby Penguin                  0
                             Dwarf Penguin               200
                             Jackass Penguin             500
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
            if player_ctx.coins(str(author.id)) < rank_costs[new_index][0]:
                await ctx.send(embed=_embed_message("Not enough coins!"))
                return
            player_ctx.setrank(str(author.id), rank_names[new_index])
            player_ctx.addCoins(str(author.id), -rank_costs[new_index][0])
            embed = discord.Embed(description=f"{author.mention} Congratulations your new rank is "
                                              f"\"{player_ctx.rank(str(author.id))}\"!", colour=colour.Colour.gold())
            await ctx.send(embed=embed)


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

    def _embed_message(message: str) -> discord.Embed:
        return discord.Embed(description=message)

    def _embed_error_message(message: str) -> discord.Embed:
        return discord.Embed(description=message, colour=colour.Colour.red())

    class RPS(commands.Cog):
        _GAMES: collections.Mapping[str, Type[games.AbstractGame]]
        _RPS = ["r", "p", "s"]

        def __init__(self):
            self._active_games = []
            self._game_offers = []

        def _get_game(self, player: discord.User):  # -> Optional[List[Any]]:
            return discord.utils.find(lambda g: g._contains_player(player), self._active_games)

        def _get_game_offer(self, player: discord.User):
            return discord.utils.find(lambda go: go._contains_player(player), self._game_offers)

        @commands.command(help='challenge user to rock-paper-scissors\n@mention the user you want to challenge')
        async def new(self, ctx: commands.Context, amount: int):
            if amount is None:
                await ctx.send(embed=_embed_error_message("Please specify the amount of  :coin:  you want to play for!"))
                return
            # if ctx.message.mention_everyone:
            #     mentions = ctx.guild.members
            #     print("everyone")
            # else:
            #     roles = ctx.message.role_mentions
            #     channels = ctx.message.channel_mentions
            #     mentions: set = ctx.message.mentions
            #     for role in roles:
            #         mentions += role.members
            #     for channel in channels:
            #         mentions += channel.members
            # print(mentions)
            mentions = ctx.message.mentions
            if mentions is None:
                await ctx.send(embed=_embed_error_message("You didn't mention an opponent!"))
                return
            player1: discord.User = ctx.author
            # if len(mentions) == 1:
            #     player2: discord.User = mentions[0]
            #     player2coins: int = player_ctx.coins(str(player2.id))
            #     if player2coins < amount:
            #         await ctx.send(embed=_embed_error_message(f"{player2.display_name} only has {player2coins}  :coin:"))
            #         return
            # else:
            #     # candidats = [m for m in mentions if player_ctx.coins(str(m.id)) >= amount]
            #     for m in mentions:
            #         print(player_ctx.coins(str(m.id)))
            #     filter(lambda men: player_ctx.coins(str(men.id)) >= amount, mentions)
            #     print(mentions)
            #     if mentions is None:
            #         await ctx.send(embed=_embed_error_message("There is no one in this group who has enough  :coin:"))
            #         return
            #     else:
            #         player2: discord.User = mentions[random.randint(0, len(mentions) - 1)]
            player1coins: int = player_ctx.coins(str(player1.id))
            player2: discord.User = mentions[random.randint(0, len(mentions) - 1)]
            if player2 is None:
                await ctx.send(embed=_embed_error_message("Sorry, failed to find opponent!"))
                return
            player2coins: int = player_ctx.coins(str(player2.id))
            if player2coins < amount:
                await ctx.send(embed=_embed_error_message(f"{player2.display_name} only has {player2coins}  :coin:"))
            elif player1coins < amount:
                await ctx.send(embed=_embed_error_message(f"You only have {player1coins}  :coin:"))
            elif self._get_game(player1) is not None:
                await ctx.send(embed=_embed_error_message("You have to finish your current game before starting a new one!"))
            elif self._get_game(player2) is not None:
                await ctx.send(embed=_embed_error_message(f"{player2.display_name} is already in a game!"))
            else:
                self._game_offers.append(RPSGame(channel=ctx.channel, player1=player1, player2=player2, coins=amount))
                await ctx.send(embed=_embed_message(f"{player2.mention}\n {player1.display_name} challenges you to a game of\n"
                                                    f"Rock, Paper, Scissors for {amount}  :coin: !\n"
                                                    f"[rps!accept/rps!decline]"))

        @commands.command(help='accept a game offer')
        async def accept(self, ctx: commands.Context):
            author: discord.User = ctx.author
            if self._get_game(author) is not None:
                await ctx.send(embed=_embed_error_message("You have to finish your current game before starting a new one!"))
            else:
                offer = discord.utils.find(lambda go: go.p2 == author, self._game_offers)
                if offer is None:
                    await ctx.send(embed=_embed_error_message("There is no offer for you to accept."))
                else:
                    self._active_games.append(offer)
                    self._game_offers.remove(offer)
                    await offer.channel.send(embed=_embed_message(
                        f"Game between {offer.player1.display_name} and {offer.player2.display_name} "
                        f"started.\nThere are {offer.coins}  :coin:  on the line!"))
                    message = _embed_message("Please make your move here with rps!play [r/p/s]")
                    await offer.player1.send(embed=message)
                    await offer.player2.send(embed=message)

        @commands.command(help='decline a game offer')
        async def decline(self, ctx: commands.Context):
            author: discord.User = ctx.author
            offer = discord.utils.find(lambda go: go.p2 == author, self._game_offers)
            if offer is None:
                await ctx.send(embed=_embed_error_message("There is no offer for you to decline."))
            else:
                self._game_offers.remove(offer)
                await offer.channel.send(embed=_embed_message(
                    f"{offer.player1.mention} {author.display_name} declined your offer."))

        @commands.command(help='pick your move for rock paper scissors (r/p/s)')
        async def play(self, ctx: commands.Context, symbol: str = None):
            if symbol is None:
                await ctx.send(embed=_embed_error_message("You didn't choose [r]ock, [p]aper or [s]cissors!"))
                return
            author: discord.User = ctx.author
            game = self._get_game(author)
            if game is None:
                await ctx.send(embed=_embed_error_message("You aren't currently in a game!"))
                return
            # else:
            #    await ctx.message.delete()

            embed = discord.Embed(title=author.display_name, description="\""+player_ctx.rank(str(author.id))+"\"")
            embed.set_thumbnail(url=author.avatar_url)
            embed.set_image(url=_rps_emoji(symbol))

            if game.move1 is not None:
                if game.move1.player == author:
                    await ctx.send("You have already made your move!")
                    return
                game.move2 = RPSMove(player=author, symbol=symbol)
                game.embed2 = embed
                await game.channel.send(embed=game.embed1)
                await game.channel.send(embed=embed)

                other = RPS._RPS.index(game.move1.symbol)
                current = RPS._RPS.index(symbol)
                if (other + 1) % 3 == current:
                    player_ctx.addCoins(str(game.move1.player.id), -game.coins)
                    player_ctx.addCoins(str(author.id), game.coins)
                    await game.channel.send(embed=_embed_message(
                        f"{author.display_name} has won {game.coins} :coin:"))
                    # win_message = discord.Embed(description=player_ctx.win_message(str(author.id)))
                    # win_message.set_thumbnail(author.avatar_url)
                    # await game.channel.send(win_message)
                elif (other - 1) % 3 == current:
                    player_ctx.addCoins(str(author.id), -game.coins)
                    player_ctx.addCoins(str(game.move1.player.id), game.coins)
                    await game.channel.send(embed=_embed_message(
                        f"{game.move1.player.display_name} has won {game.coins} :coin:"))
                    # win_message = discord.Embed(description=player_ctx.win_message(str(game[0].id)))
                    # win_message.set_thumbnail(game[0].avatar_url)
                    # await game.channel.send(win_message)
                else:
                    await game.channel.send(embed=_embed_message("It's a draw :handshake:"))
                self._active_games.remove(game)
            else:
                game.move1 = RPSMove(player=author, symbol=symbol)
                game.embed1 = embed
                await game.channel.send(embed=_embed_message(f"{author.display_name} has made a move"))

        @commands.command(help='cancel your current outgoing game challenge')
        async def cancel(self, ctx: commands.Context) -> None:
            author: discord.User = ctx.author
            offer = discord.utils.find(lambda go: go.p1 == author, self._game_offers)
            if offer is None:
                await ctx.send(embed=_embed_error_message("Please offer a game first!"))
            else:
                self._game_offers.remove(offer)
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
