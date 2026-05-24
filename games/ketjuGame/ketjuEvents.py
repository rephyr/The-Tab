from dataclasses import dataclass


@dataclass
class KetjuCardDrawnEvent:
    player: str
    card: str
    previousCard: str
    guess: str        # "korkeampi" or "matalampi"
    correct: bool
    streak: int       # new streak if correct, streak before draw if wrong
    pot: int
    multiplier: int


@dataclass
class KetjuEqualCardEvent:
    player: str
    card: str
    previousCard: str
    penalty: int
    multiplier: int
    total: int


@dataclass
class KetjuDoubleOrDoubleEvent:
    player: str
    challengeCard: str
    previousCard: str
    guess: str
    correct: bool
    pot: int
    multiplier: int
    amount: int   # drinks given (correct) or drunk (wrong)


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
