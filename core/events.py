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
class GameEndEvent:
    scores: list
    timestamp: datetime = field(default_factory=datetime.now)
