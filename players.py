import os
from typing import Tuple, Optional

import psycopg2
from psycopg2.extensions import connection, cursor

_DBNAME = os.environ["BOT_DB_NAME"]
_DBUSER = os.environ["BOT_DB_USER"]
_DBPASS = os.environ["BOT_DB_PASS"]
_DBHOST = os.getenv("BOT_DB_HOST", "localhost")
_DBPORT = os.getenv("BOT_DB_PORT", "5432")


class context:
    _con: connection
    _cur: cursor

    def __init__(self):
        pass

    def __enter__(self) -> "context":
        self._con = psycopg2.connect(database=_DBNAME,
                                     user=_DBUSER,
                                     password=_DBPASS,
                                     host=_DBHOST,
                                     port=_DBPORT)
        self._con.autocommit = True
        self._cur = self._con.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cur.close()
        self._con.close()

    def _create_player(self, player_id: str):
        print("CREATING PLAYER")
        self._cur.execute("INSERT INTO players (id, rank, coins) "
                          "VALUES (%s, %s, %s)", (player_id, 'Beginner', 0))

    def coins(self, player_id: str) -> int:
        self._cur.execute("SELECT coins "
                          "FROM players "
                          "WHERE id = %s", (player_id,))
        result: Optional[Tuple[int]] = self._cur.fetchone()
        if result is None:
            self._create_player(player_id)
            return 0
        else:
             return result[0]
        
    def addCoins(self, player_id: str, amount: int) -> None:
        newamount = max(0, amount + self.coins(player_id))
        self._cur.execute("""UPDATE players
                          SET coins = %s
                          WHERE id = %s""", (str(newamount), player_id))

    def newrank(self, player_id: str, rank: str) -> None:
        self._cur.execute("""UPDATE players
                            SET rank = %s
                            WHERE id = %s"""), (rank, player_id)

    def rank(self, player_id: str) -> str:
        self._cur.execute("SELECT rank "
                          "FROM players "
                          "WHERE id = %s", (player_id,))
        result: Optional[Tuple[str]] = self._cur.fetchone()
        if result is None:
            self._create_player(player_id)
            return "Beginner"
        else:
            return result[0]

    def randc(self, player_id: str):
        self._cur.execute("""SELECT rank, coins
                             FROM players
                             WHERE id = %s"""), (player_id)
        result: Optional[Tuple[str, int]] = self._cur.fetchone()
        if result is None:
            self._create_player(player_id)
            return 0
        else:
            return result
