from dataclasses import dataclass
from typing import Optional


@dataclass
class KetjuCardDrawnEvent:
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
class KetjuEqualCardEvent:
    player: str
    card: str
    previousCard: str
    penalty: int
    multiplier: int
    total: int
    chainedPlayer: Optional[str] = None


@dataclass
class KetjuDoubleOrDoubleEvent:
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
class KetjuExitEvent:
    player: str
    pot: int
    streak: int


@dataclass
class KetjuLinkResolvedEvent:
    linkedPlayer: str
    triggerPlayer: str
    amount: int
