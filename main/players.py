import os
import psycopg2
from psycopg2.extensions import connection, cursor

_DBNAME = os.environ["BOT_DB_NAME"]
_DBUSER = os.environ["BOT_DB_USER"]
_DBPASS = os.environ["BOT_DB_PASS"]
_DBHOST = os.environ["BOT_DB_HOST"] or "localhost"
_DBPORT = os.environ["BOT_DB_PORT"] or "5432"


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
        self._cur = self._con.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cur.close()
        self._con.close()

    def coins(self, player_id: str) -> int:
        self._cur.execute("SELECT coins "
                          "FROM players "
                          "WHERE id = %s", (player_id,))
        return self._cur.fetchone()[0]

    def rank(self, player_id: str) -> str:
        self._cur.execute("SELECT rank "
                          "FROM players "
                          "WHERE id = %s", (player_id,))
        return self._cur.fetchone()[0]
