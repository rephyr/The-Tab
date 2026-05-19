"""
Events emitted by the game during play. The GameLog collects these and
converts them to a structured dict for the formatter to use.

GameStartEvent   — fired once at the start with the player list
PhaseEvent       — fired at the start of each player's turn in a phase,
                   and once with an empty player name when the board phase begins
GuessEvent       — fired after a card is drawn; guess and correct may be None for edge cases
DrinkEvent       — fired whenever someone has to drink
GiveEvent        — fired when a player gives drinks to someone else
ShareEvent       — fired when two players share drinks (board phase only)
BoardCardEvent   — fired when a board card is revealed
GameEndEvent     — fired once at the end with final scores
"""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class GameStartEvent:
    players: list
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PhaseEvent:
    phase: str
    player: str


@dataclass
class GuessEvent:
    player: str
    phase: str
    guess: str
    card: str
    correct: bool


@dataclass
class DrinkEvent:
    player: str
    amount: int
    reason: str


@dataclass
class GiveEvent:
    giver: str
    receiver: str
    amount: int


@dataclass
class ShareEvent:
    player1: str
    player2: str
    amount: int


@dataclass
class BoardCardEvent:
    card: str
    action: str
    drinks: int
    matched: list

@dataclass
class BoardCardDoneEvent:
    pass

@dataclass
class RouletteResultEvent:
    player: str
    hit: bool
    drinks: int


@dataclass
class TaskDrawEvent:
    drawer: str
    title: str
    description: str
    targets: list

21
@dataclass
class GameEndEvent:
    scores: list
    timestamp: datetime = field(default_factory=datetime.now)
