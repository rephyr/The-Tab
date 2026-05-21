"""Generates randomised Horse instances with stats and relative odds for RavitGame."""
import random
from dataclasses import dataclass

HORSE_NAMES = [
    "Ukko", "Tuulikki", "Rauhala", "Pitkämäki","Laukki", "Talvikki",
    "Salamaveto", "Myrsky", "Loimu", "Varjo", "Halla", "Aava", "Vauhti", "Arkku",
    "Takuu", "Lehmä", "Mönkiä", "Iso", "Taika", "Velho", "Veto", "Panos",
    "Turbovauhti", "Pikaliito", "Ässä", "Hurjapää", "Voittamaton", "Häviämätön",
    "Tulikavio", "Viesker", "Pata", "Risti", "Arpa", "Saamaton", "Ahdin",
    "Lötinä", "Täräyttäjä","Massikeisari", "Vetäjä", "Työntö", "Jabin"
]


@dataclass
class Horse:
    """
    Single horse entry. All mutable fields are updated in-place during the race.

    Fields set at creation — id, name, speed, endurance, luck, odds, fightStrength,
    fightMaxHealth, staminaLeft.

    Fields mutated during the race — position, status, tiredRoundsLeft,
    stumbleRoundsLeft, motivatedRoundsLeft, fightRoundsLeft, fightOpponent,
    fightHealth, confusedRoundsLeft, staminaLeft.

    status — "racing" | "dnf" | "dead"
    fightOpponent — id of current fight opponent, or None
    """
    id: int
    name: str
    speed: int
    endurance: int
    luck: int
    odds: float = 0.0
    position: int = 0
    status: str = "racing"
    tiredRoundsLeft: int = 0
    stumbleRoundsLeft: int = 0
    motivatedRoundsLeft: int = 0
    fightRoundsLeft: int = 0
    fightOpponent: int = None
    fightStrength: int = 0
    fightMaxHealth: int = 0
    fightHealth: int = 0
    confusedRoundsLeft: int = 0
    staminaLeft: int = 0

    def toDict(self) -> dict:
        """Return all fields as a plain dict for event payloads and receipt formatters."""
        return {
            "id": self.id, "name": self.name,
            "speed": self.speed, "endurance": self.endurance, "luck": self.luck,
            "odds": self.odds, "position": self.position, "status": self.status,
            "tiredRoundsLeft": self.tiredRoundsLeft,
            "stumbleRoundsLeft": self.stumbleRoundsLeft,
            "motivatedRoundsLeft": self.motivatedRoundsLeft,
            "fightRoundsLeft": self.fightRoundsLeft,
            "fightOpponent": self.fightOpponent,
            "fightStrength": self.fightStrength,
            "fightMaxHealth": self.fightMaxHealth,
            "fightHealth": self.fightHealth,
            "confusedRoundsLeft": self.confusedRoundsLeft,
            "staminaLeft": self.staminaLeft,
        }


def _generateHorse(horseId: int, name: str) -> Horse:
    speed = random.randint(1, 5)
    endurance = random.randint(1, 5)
    luck = random.randint(1, 5)
    return Horse(
        id=horseId, name=name,
        speed=speed, endurance=endurance, luck=luck,
        fightStrength=random.randint(5, 10),
        fightMaxHealth=random.randint(15, 30),
        staminaLeft=endurance * 3,
    )


def _assignRelativeOdds(horses: list) -> None:
    totals = [h.speed + h.endurance + h.luck for h in horses]
    minT, maxT = min(totals), max(totals)
    for h, total in zip(horses, totals):
        if maxT == minT:
            base = 3.5
        else:
            t = (total - minT) / (maxT - minT)
            base = 8.0 - t * 6.5
        h.odds = max(1.5, round(base * random.uniform(0.85, 1.25), 1))


def generateHorses(count: int) -> list:
    count = min(count, len(HORSE_NAMES))
    names = random.sample(HORSE_NAMES, count)
    horses = [_generateHorse(i + 1, name) for i, name in enumerate(names)]
    _assignRelativeOdds(horses)
    return horses
