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

@dataclass
class TaskDrinkSummaryEvent:
    scores: list  # [{"name": str, "drank": int, "toGive": int}, ...]

@dataclass
class TaskChainStartEvent:
    drawer: str
    title: str
    description: str
    assignments: list  # [{"name": str, "amount": int, "cascades": [{"name", "amount", "reason"}]}]

@dataclass
class GameEndEvent:
    scores: list
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RaceRoundEvent:
    roundNumber: int
    trackLength: int
    positions: list   # [{"id", "name", "position", "status", "tiredRoundsLeft", "stumbleRoundsLeft"}, ...]
    raceEvents: list  # [{"horseName", "eventType", "detail"}, ...] events that fired this round


@dataclass
class RaceStartEvent:
    players: list
    horses: list
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class BetsPlacedEvent:
    horses: list
    bets: list


@dataclass
class HorseEventFiredEvent:
    roundNumber: int
    horseId: int
    horseName: str
    eventType: str
    detail: str


@dataclass
class RaceFinishedEvent:
    roundNumber: int
    finalPositions: list


@dataclass
class TiebreakStartEvent:
    combatants: list  # [{"id", "name", "odds", "health", "maxHealth", "strength"}, ...]


@dataclass
class TiebreakRoundEvent:
    roundNumber: int
    combatants: list  # [{"name", "health", "maxHealth", "strength"}, ...] state after damage


@dataclass
class TiebreakEliminationEvent:
    loserName: str
    remaining: list       # names still in the fight
    combatants: list      # [{"name", "health", "maxHealth", "strength"}, ...] full state incl. loser at 0 HP


@dataclass
class TiebreakWinnerEvent:
    winnerName: str
    health: int
    maxHealth: int
    strength: int
