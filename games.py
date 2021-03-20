import enum
import abc
from typing import Dict, Set
import cards

import discord
import discord.ext.commands as commands


class GameRegisterResult(enum.Enum):
    SUCCESS = enum.auto()
    CAPACITY_REACHED = enum.auto()
    ALREADY_REGISTERED = enum.auto()
    REGISTRATION_ERROR = enum.auto()


class AbstractGame(abc.ABC):

    def __init__(self, capacity: int) -> None:
        self._capacity: int = capacity
        self._players: Set[str] = set()

    @abc.abstractmethod
    def _init_player(self, player_id) -> bool:
        pass

    def register_player(self, player_id: str) -> GameRegisterResult:
        if player_id in self._players:
            return GameRegisterResult.ALREADY_REGISTERED
        elif self._capacity >= len(self._players):
            return GameRegisterResult.GAME_FULL
        else:
            return GameRegisterResult.SUCCESS if self._init_player(player_id) else GameRegisterResult.REGISTRATION_ERROR


class Blackjack(AbstractGame):

    def __init__(self):
        super().__init__(4)
        self._player_cards: Dict[str, cards.MultiPlayingCardCollection] = {}
        self._bank_stats: int = 0
        self._card_deck: cards.MultiPlayingCardCollection = cards.mdeck(cards.cards())

    @classmethod
    def help(cls) -> str:
        return 'Play a classic game of Blackjack!'

    def _init_player(self, player_id) -> bool:
        self._player_cards[player_id] = cards.mdeck_empty()
        return True
