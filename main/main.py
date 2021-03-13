import players

with players.context() as ctx:
    print(ctx.coins("1"))
    print(ctx.rank("1"))
