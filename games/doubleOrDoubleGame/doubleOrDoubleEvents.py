from dataclasses import dataclass
from typing import Optional


@dataclass
class DoDTurnStartEvent:
    player: str
    previousCard: str
    streak: int
    pot: int
    multiplier: int
    chainedPlayer: Optional[str] = None


@dataclass
class DoDCardDrawnEvent:
    player: str
    card: str
    previousCard: str
    guess: str                           # Higher or Lower
    correct: bool
    streak: int                          # new streak if correct, streak before draw if wrong
    pot: int
    multiplier: int
    chainedPlayer: Optional[str] = None  # set when wrong guess and a chain is active


@dataclass
class DoDEqualCardEvent:
    player: str
    card: str
    previousCard: str
    penalty: int
    multiplier: int
    total: int
    chainedPlayer: Optional[str] = None


@dataclass
class DoDChallengeEvent:
    player: str
    challengeCard: str
    previousCard: str
    guess: str
    correct: bool
    pot: int
    multiplier: int
    amount: int                          # drinks given (correct) or drunk (wrong):
    chainedPlayer: Optional[str] = None  # set when wrong guess and a chain is active
    target: Optional[str] = None         # set on correct guess: who receives the drinks


@dataclass
class DoDExitEvent:
    player: str
    pot: int
    streak: int


@dataclass
class DoDLinkResolvedEvent:
    linkedPlayer: str
    triggerPlayer: str
    amount: int
