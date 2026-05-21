"""Generates randomised horses with stats and relative odds for RavitGame."""
import random

HORSE_NAMES = [
    "Ukko", "Tuulikki", "Rauhala", "Pitkämäki","Laukki", "Talvikki", 
    "Salamaveto", "Myrsky", "Loimu", "Varjo", "Halla", "Aava", "Vauhti", "Arkku",
    "Takuu", "Lehmä", "Mönkiä", "Iso", "Taika", "Velho", "Veto", "Panos",
    "Turbovauhti", "Pikaliito", "Ässä", "Hurjapää", "Voittamaton", "Häviämätön",
    "Tulikavio", "Viesker", "Pata", "Risti", "Arpa", "Saamaton", "Ahdin", 
    "Lötinä", "Täräyttäjä","Massikeisari", "Vetäjä", "Työntö", 
]


def _generateHorse(horseId: int, name: str) -> dict:
    speed = random.randint(1, 5)
    endurance = random.randint(1, 5)
    luck = random.randint(1, 5)
    return {
        "id": horseId,
        "name": name,
        "speed": speed,
        "endurance": endurance,
        "luck": luck,
        "odds": 0.0,
        "position": 0,
        "status": "racing",
        "tiredRoundsLeft": 0,
        "stumbleRoundsLeft": 0,
        "motivatedRoundsLeft": 0,
        "fightRoundsLeft": 0,
        "fightOpponent": None,
        "fightStrength": random.randint(5, 10),
        "fightMaxHealth": random.randint(15, 30),
        "fightHealth": 0,
        "confusedRoundsLeft": 0,
        "staminaLeft": endurance * 3,
    }


def _assignRelativeOdds(horses: list) -> None:
    totals = [h["speed"] + h["endurance"] + h["luck"] for h in horses]
    minT, maxT = min(totals), max(totals)
    for h, total in zip(horses, totals):
        if maxT == minT:
            base = 3.5
        else:
            t = (total - minT) / (maxT - minT)  # 0 = weakest, 1 = strongest
            base = 8.0 - t * 6.5                    # weakest → 8.0, strongest → 1.5
        h["odds"] = max(1.5, round(base * random.uniform(0.85, 1.25), 1))


def generateHorses(count: int) -> list:
    names = random.sample(HORSE_NAMES, count)
    horses = [_generateHorse(i + 1, name) for i, name in enumerate(names)]
    _assignRelativeOdds(horses)
    return horses
