import discord
import discord.ext.commands as commands
import players
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
            pass

        @commands.command()
        async def coins(self, ctx: commands.Context):
            author: discord.User = ctx.author
            #if author := ctx.author is not discord.User:
                #return
            await ctx.send(f"```@{author.display_name}, your current balance is {player_ctx.coins(str(author.id))}```")

        @commands.command()
        async def rank(self, ctx: commands.Context):
            author: discord.User = ctx.author
            #if author := ctx.author is not discord.User:
                #return
            await ctx.send(f"```@{author.display_name}, your current rank is {player_ctx.rank(str(author.id))}```")

        @commands.command()
        async def new(self, ctx: commands.Context, amount: int):
            author: discord.User = ctx.author
            p2 = ctx.message.mentions[random.randint(0, len(ctx.message.mentions) - 1)]
            p1coins = player_ctx.coins(str(author.id))
            if p1coins < amount:
                await ctx.send(f"```@{author.display_name}, you only have {p1coins} coins```")
                return
            p2coins = player_ctx.coins(str(p2.id))
            if p2coins < amount:
                await ctx.send(f"```@{p2.display_name}, you only have {p2coins} coins```")
                return
            if p2 is None:
                await ctx.send(f"```Sorry, can't find player {ctx.message.split(' ')[1]}```")
                return
            if getgame(author) is None and getgame(p2) is None:
                games.append([author, p2, amount])
                await ctx.send(f"```@{p2.name}, do you accept the game with {author.display_name}? [bj!accept/bj!decline]")
                await ctx.send(f"```Game between @{author.display_name} and @{p2.name} started.\nThere are {amount} coins on the line```")
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
                    await ctx.send(f"```@{author} has won```")
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

        @commands.command()
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

        async def bj(self, ctx: commands.Context):


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
