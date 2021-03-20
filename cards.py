import enum
import random
from collections import Iterable, Mapping, Callable, Iterator, MutableSet, MutableSequence


class PlayingCardSuite(enum.Enum):
    DIAMOND = enum.auto()
    CLUB = enum.auto()
    HEART = enum.auto()
    SPADE = enum.auto()


class PlayingCardValue(enum.IntEnum):
    TWO = 0
    THREE = 1
    FOUR = 2
    FIVE = 3
    SIX = 4
    SEVEN = 5
    EIGHT = 6
    NINE = 7
    TEN = 8
    JACK = 9
    QUEEN = 10
    KING = 11
    ACE = 12


class PlayingCard:

    def __init__(self, suit: PlayingCardSuite, value: PlayingCardValue, secret: object) -> None:
        if secret is not _SECRET:
            raise RuntimeError("PlayingCard should not be instantiated outside of the util.py module.")
        self._suit = suit
        self._value = value

    def suit(self) -> PlayingCardSuite:
        return self._suit

    def value(self) -> PlayingCardSuite:
        return self._suit


class UniquePlayingCardCollection(MutableSet[PlayingCard]):

    def __init__(self, source: MutableSet[PlayingCard], secret: object) -> None:
        if secret is not _SECRET:
            raise RuntimeError("UniquePlayingCardDeck should not be instantiated outside of the util.py module.")
        self._cards = source

    def draw(self) -> PlayingCard:
        result: PlayingCard = random.choice(tuple(self._cards))
        self._cards.remove(result)
        return result

    def add(self, value: PlayingCard) -> None:
        self._cards.add(value)

    def discard(self, value: PlayingCard) -> None:
        self._cards.discard(value)

    def __iter__(self) -> Iterator[PlayingCard]:
        return self._cards.__iter__()

    def __contains__(self, __x: object) -> bool:
        return self._cards.__contains__(__x)

    def __len__(self) -> int:
        return self._cards.__len__()


class MultiPlayingCardCollection(MutableSequence[PlayingCard]):

    def __init__(self, source: MutableSequence[PlayingCard], secret: object) -> None:
        if secret is not _SECRET:
            raise RuntimeError("MultiPlayingCardDeck should not be instantiated outside of the util.py module.")
        self._cards: MutableSequence[PlayingCard] = source

    def draw(self) -> PlayingCard:
        result_idx: int = random.randrange(0, len(self._cards))
        self._cards.pop(result_idx)
        return self._cards[result_idx]

    def insert(self, index: int, value: PlayingCard) -> None:
        self._cards.insert(index, value)

    def __getitem__(self, i: int) -> PlayingCard:
        return self._cards.__getitem__(i)

    def __setitem__(self, i: int, o: PlayingCard) -> None:
        self._cards.__setitem__(i, o)

    def __delitem__(self, i: int) -> None:
        self._cards.__delitem__(i)

    def __len__(self) -> int:
        return self._cards.__len__()


_SECRET = object()
_CARDS: Mapping[PlayingCardSuite, Mapping[PlayingCardValue, "PlayingCard"]] = \
    {suite: {value: PlayingCard(suite, value, _SECRET) for value in PlayingCardValue} for suite in PlayingCardSuite}


def card(suit: PlayingCardSuite, value: PlayingCardValue) -> PlayingCard:
    return _CARDS[suit][value]


def cards() -> Iterable[PlayingCard]:
    return {c for c in {cs.values() for cs in _CARDS.values()}}


def cards_by_suit(suit: PlayingCardSuite) -> Iterable[PlayingCard]:
    return _CARDS[suit].values()


def cards_by_value(value: PlayingCardValue) -> Iterable[PlayingCard]:
    return {cs[value] for cs in _CARDS.values()}


def cards_by_predicate(predicate: Callable[[PlayingCard], bool]) -> Iterable[PlayingCard]:
    return {c for c in {cs.values() for cs in _CARDS.values()} if predicate(c)}


def udeck(source: Iterable[PlayingCard]) -> UniquePlayingCardCollection:
    return UniquePlayingCardCollection(set(source), _SECRET)


def udeck_from_individuals(*source: PlayingCard) -> UniquePlayingCardCollection:
    return UniquePlayingCardCollection(set(source), _SECRET)


def udeck_empty() -> UniquePlayingCardCollection:
    return UniquePlayingCardCollection(set(), _SECRET)


def mdeck(source: Iterable[PlayingCard]) -> MultiPlayingCardCollection:
    return MultiPlayingCardCollection(list(source), _SECRET)


def mdeck_from_individuals(*source: PlayingCard) -> MultiPlayingCardCollection:
    return MultiPlayingCardCollection(list(source), _SECRET)


def mdeck_empty() -> MultiPlayingCardCollection:
    return MultiPlayingCardCollection([], _SECRET)
