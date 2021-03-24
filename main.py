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

    class RPSMove:
        def __init__(self, player=None, symbol: str = None):
            self.player = player
            self.symbol = symbol
            pass

    class RPSGame:
        def __init__(self, channel=None, p1: discord.User = None, p2: discord.User = None, coins: int = 0,
                     move1: RPSMove = None, move2: RPSMove = None,
                     embed1: discord.Embed = None, embed2: discord.Embed = None):
            self.channel = channel
            self.p1 = p1
            self.p2 = p2
            self.coins = coins
            self.move1 = move1
            self.move2 = move2
            self.embed1 = embed1
            self.embed2 = embed2
            pass

        def _contains_player(self, player) -> bool:
            return self.p1 == player or self.p2 == player

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
                # varchar(20) isn't enough for some names
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
            return discord.utils.find(lambda g: g._contains_player(player), self._active_games)

        def _get_game_offer(self, player: discord.User):
            return discord.utils.find(lambda go: go._contains_player(player), self._game_offers)

        @commands.command(help='challenge user to rock-paper-scissors\n@mention the user you want to challenge')
        async def new(self, ctx: commands.Context, amount: int):
            if amount is None:
                embed = discord.Embed(description="Please specify the amount of  :coin:  you want to play for!")
                await ctx.send(embed=embed)
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
                await ctx.send(embed=_embed_message("You didn't mention an opponent!"))
                return
            p1: discord.User = ctx.author
            # if len(mentions) == 1:
            #     p2: discord.User = mentions[0]
            #     p2coins: int = player_ctx.coins(str(p2.id))
            #     if p2coins < amount:
            #         embed = discord.Embed(description=f"{p2.display_name} only has {p2coins}  :coin:")
            #         await ctx.send(embed=embed)
            #         return
            # else:
            #     # candidats = [m for m in mentions if player_ctx.coins(str(m.id)) >= amount]
            #     for m in mentions:
            #         print(player_ctx.coins(str(m.id)))
            #     filter(lambda men: player_ctx.coins(str(men.id)) >= amount, mentions)
            #     print(mentions)
            #     if mentions is None:
            #         await ctx.send(embed=_embed_message("There is no one in this group who has enough  :coin:"))
            #         return
            #     else:
            #         p2: discord.User = mentions[random.randint(0, len(mentions) - 1)]
            p1coins: int = player_ctx.coins(str(p1.id))
            p2: discord.User = mentions[random.randint(0, len(mentions) - 1)]
            if p2 is None:
                await ctx.send(embed=_embed_message("Sorry, failed to find opponent!"))
                return
            p2coins: int = player_ctx.coins(str(p2.id))
            if p2coins < amount:
                embed = discord.Embed(description=f"{p2.display_name} only has {p2coins}  :coin:")
                await ctx.send(embed=embed)
            elif p1coins < amount:
                await ctx.send(embed=_embed_message(f"You only have {p1coins}  :coin:"))
            elif self._get_game(p1) is not None:
                await ctx.send(embed=_embed_message("You have to finish your current game before starting a new one!"))
            elif self._get_game(p2) is not None:
                await ctx.send(embed=_embed_message(f"{p2.display_name} is already in a game!"))
            else:
                self._game_offers.append(RPSGame(channel=ctx.channel, p1=p1, p2=p2, coins=amount))
                await ctx.send(embed=_embed_message(f"{p2.mention}\n {p1.display_name} challenges you to a game of\n"
                                                    f"Rock, Paper, Scissors for {amount}  :coin: !\n"
                                                    f"[rps!accept/rps!decline]"))

        @commands.command(help="accept a game offer")
        async def accept(self, ctx: commands.Context):
            author: discord.User = ctx.author
            if not self._get_game(author) is None:
                await ctx.send(embed=_embed_message("You have to finish your current game before starting a new one."))
            else:
                offered = self._get_game_offer(author)
                if offered is None:
                    await ctx.send(embed=_embed_message("There is no offer for you to accept."))
                else:
                    self._active_games.append(offered)
                    self._game_offers.remove(offered)
                    await offered.channel.send(embed=_embed_message(
                        f"Game between {offered.p1.display_name} and {offered.p2.display_name} "
                        f"started.\nThere are {offered.coins}  :coin:  on the line!"))
                    await offered.p1.send(embed=_embed_message("Please make your move here with rps!play [r/p/s]"))
                    await offered.p2.send(embed=_embed_message("Please make your move here with rps!play [r/p/s]"))

        @commands.command("decline a game offer")
        async def decline(self, ctx: commands.Context):
            author: discord.User = ctx.author
            offered = self._get_game_offer(author)
            if offered is None:
                await ctx.send(embed=_embed_message("There is no offer for you to decline."))
            else:
                self._game_offers.remove(offered)
                await offered.channel.send(embed=_embed_message(
                    f"{offered.p1.mention} {author.display_name} declined your offer."))

        @commands.command(help='pick your move for rock paper scissors (r/p/s)')
        async def play(self, ctx: commands.Context, symbol: str):
            author: discord.User = ctx.author
            game = self._get_game(author)
            if game is None:
                await ctx.send(embed=_embed_message("You aren't currently in a game!"))
                return
            # else:
            #    await ctx.message.delete()

            embed = discord.Embed(title=author.display_name, description="\""+player_ctx.rank(str(author.id))+"\"")
            embed.set_thumbnail(url=author.avatar_url)
            embed.set_image(url=_rps_emoji(symbol))

            if game.move1 is not None:
                game.move2 = RPSMove(player=author, symbol=symbol)
                game.embed2 = embed
                await game.channel.send(embed=game.embed1)
                await game.channel.send(embed=embed)

                other = RPS._RPS.index(game.move1.symbol)
                current = RPS._RPS.index(symbol)
                if (other + 1) % 3 == current:
                    player_ctx.addCoins(str(game.move1.player.id), -game.coins)
                    player_ctx.addCoins(str(author.id), game.coins)
                    await game.channel.send(embed=_embed_message(f"{author.display_name} has won {game.coins} :coin:"))
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
