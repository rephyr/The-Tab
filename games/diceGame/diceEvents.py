from dataclasses import dataclass


@dataclass
class MexicanRollEvent:
    player: str
    d1: int
    d2: int
    actual: int
    claimed: int


@dataclass
class MexicanChallengeEvent:
    challenger: str
    claimer: str
    claimed: int
    actual: int
    d1: int
    d2: int
    loser: str
    drinks: int
    wasMexico: bool


@dataclass
class MexicanAcceptEvent:
    accepter: str
    claimed: int
