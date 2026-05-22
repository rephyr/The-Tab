"""Jockey cards for RavitGame. Each card grants a passive bonus to the assigned horse.

To add a new jockey: append a Jockey entry to JOCKEYS. Stat bonuses are applied
immediately via applyToHorse(). Behavioral flags are read by RavitGame during the race:
  immuneToFights       — horse is skipped when _checkNewFights looks for pairs
  eventChanceMultiplier — multiplied into baseChance in _tryFireEvent
  boostMultiplier      — multiplied into boost distance in _eventBoost
"""
import random
from dataclasses import dataclass


@dataclass
class Jockey:
    name: str
    description: str
    speedBonus: int = 0
    enduranceBonus: int = 0
    luckBonus: int = 0
    fightStrengthBonus: int = 0
    startPositionBonus: int = 0
    eventChanceMultiplier: float = 1.0
    boostMultiplier: float = 1.0
    immuneToFights: bool = False

    def applyToHorse(self, horse) -> None:
        """Apply one-time stat bonuses. Call once when jockey is assigned to a horse."""
        horse.speed         = min(5,  horse.speed         + self.speedBonus)
        horse.endurance     = min(5,  horse.endurance     + self.enduranceBonus)
        horse.luck          = min(5,  horse.luck          + self.luckBonus)
        horse.fightStrength = min(10, horse.fightStrength + self.fightStrengthBonus)
        horse.position     += self.startPositionBonus


JOCKEYS: list[Jockey] = [
    Jockey("Turbo",      "+1 nopeus",                    speedBonus=1),
    Jockey("Sitkeä",     "+1 kestävyys",                 enduranceBonus=1),
    Jockey("Tuuri",      "+1 tuuri",                     luckBonus=1),
    Jockey("Taistelija", "+2 taisteluvoimaa",            fightStrengthBonus=2),
    Jockey("Terävä",     "Lähtee 2 ruutua edellä",       startPositionBonus=2),
    Jockey("Pelkuri",    "Ei osallistu tappeluksiin",    immuneToFights=True),
    Jockey("Onnekas",    "Puolet vähemmän tapahtumia",   eventChanceMultiplier=0.5),
    Jockey("Raju",       "Boost vie tuplasti eteenpäin", boostMultiplier=2.0),
]


def dealJockeys(count: int = 2) -> list[Jockey]:
    """Return `count` unique randomly sampled jockeys."""
    return random.sample(JOCKEYS, min(count, len(JOCKEYS)))
