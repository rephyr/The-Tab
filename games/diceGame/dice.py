"""
Mexican dice bluffing drinking game (Mäxchen / Mexico).

The operator sees every roll on screen. The roller announces their score
verbally (truthfully or lying). The next player challenges or accepts.
On challenge: claimer lied → claimer drinks; claimer told truth → challenger drinks.
Mexico (2-1) is the highest value and doubles the drink penalty.
"""
import random
from dataclasses import dataclass, field
from typing import Optional

from core.game import Game
from core.events import GameStartEvent, GameEndEvent, DrinkEvent
from games.diceGame.diceEvents import MexicanRollEvent, MexicanChallengeEvent, MexicanAcceptEvent

_SEP = "=" * 32


def _scoreRoll(d1: int, d2: int) -> int:
    """Return an integer score where higher always beats lower.

    Mexico (2-1) = 1000, doubles = 201-206, regular = 31-65.
    Doubles always beat regular; Mexico beats everything.
    """
    high, low = max(d1, d2), min(d1, d2)
    if high == 2 and low == 1:
        return 1000
    if high == low:
        return 200 + high
    return high * 10 + low


def _displayScore(d1: int, d2: int) -> str:
    score = _scoreRoll(d1, d2)
    high, low = max(d1, d2), min(d1, d2)
    if score == 1000:
        return "Mexico (2-1)"
    if score > 100:
        return f"Parit ({high}-{high})"
    return f"{score} ({high}-{low})"


def _displayClaimScore(score: int) -> str:
    if score == 1000:
        return "Mexico (2-1)"
    if score > 100:
        d = score - 200
        return f"Parit ({d}-{d})"
    high = score // 10
    low = score % 10
    return f"{score} ({high}-{low})"


def _parseClaim(raw: str) -> Optional[int]:
    """Parse operator input into a score. Returns None if invalid."""
    raw = raw.strip().lower()
    if raw in ("mexico", "meksiko"):
        return 1000
    if len(raw) == 2 and raw.isdigit():
        d1, d2 = int(raw[0]), int(raw[1])
        if 1 <= d1 <= 6 and 1 <= d2 <= 6:
            return _scoreRoll(d1, d2)
    return None


@dataclass
class MexicanGame(Game):
    """Mexican dice bluffing game. One call to playRound() runs until quit."""
    gameTitle: str = "Mexico"
    config: dict = field(default_factory=dict)

    def playRound(self) -> None:
        self.emit(GameStartEvent([p.getName() for p in self.players]))

        rollerIndex = 0
        previousClaim = None

        try:
            while True:
                roller = self.players[rollerIndex % len(self.players)]

                self._showRollPrompt(roller.getName(), previousClaim)
                raw = input("").strip().lower()
                if raw == "quit":
                    break

                d1 = random.randint(1, 6)
                d2 = random.randint(1, 6)
                actual = _scoreRoll(d1, d2)

                self._clearScreen()
                claimed = self._getClaimFromOperator(roller.getName(), d1, d2, actual, previousClaim)
                if claimed is None:
                    break

                self.emit(MexicanRollEvent(roller.getName(), d1, d2, actual, claimed))

                nextIndex = (rollerIndex + 1) % len(self.players)
                challenger = self.players[nextIndex]

                self._clearScreen()
                decision = self._getChallengeDecision(roller.getName(), challenger.getName(), claimed)

                if decision == "c":
                    wasMexico = claimed == 1000 or actual == 1000
                    drinks = self._drinkAmount(wasMexico)
                    loser = roller if actual < claimed else challenger

                    loser.addDrinks(drinks)
                    self.emit(MexicanChallengeEvent(
                        challenger=challenger.getName(),
                        claimer=roller.getName(),
                        claimed=claimed,
                        actual=actual,
                        d1=d1,
                        d2=d2,
                        loser=loser.getName(),
                        drinks=drinks,
                        wasMexico=wasMexico,
                    ))
                    self.emit(DrinkEvent(loser.getName(), drinks, "mexico-haaste"))

                    self._showChallengeResult(
                        roller.getName(), challenger.getName(),
                        claimed, actual, d1, d2, loser.getName(), drinks,
                    )
                    input("\nPaina Enter jatkaaksesi...")

                    winner = roller if loser == challenger else challenger
                    rollerIndex = self.players.index(winner)
                    previousClaim = None

                else:
                    self.emit(MexicanAcceptEvent(challenger.getName(), claimed))
                    previousClaim = claimed
                    rollerIndex = nextIndex

        except KeyboardInterrupt:
            print()

        self.emit(GameEndEvent([
            {"name": p.getName(), "drinksTaken": p.getDrinksTaken(), "drinksToGive": p.drinksToGive}
            for p in self.players
        ]))

    def _drinkAmount(self, wasMexico: bool) -> int:
        if wasMexico:
            return int(self.config.get("mexicoDrinks", 2))
        return int(self.config.get("drinkAmount", 1))

    def _showRollPrompt(self, rollerName: str, previousClaim: Optional[int]) -> None:
        print("\n" + _SEP)
        if previousClaim is not None:
            print(f"  Ylitettävä: {_displayClaimScore(previousClaim)}")
        print(f"\n  >>> {rollerName.upper()} HEITTÄÄ <<<\n")
        print("  Paina Enter heittääksesi")
        print('  (tai "quit" lopettaaksesi)')
        print(_SEP)

    def _getClaimFromOperator(
        self,
        rollerName: str,
        d1: int,
        d2: int,
        actual: int,
        previousClaim: Optional[int],
    ) -> Optional[int]:
        print("\n" + _SEP)
        print(f"  Heitto: {d1} ja {d2}  —  {_displayScore(d1, d2)}")
        if previousClaim is not None:
            print(f"  Pitää ylittää: {_displayClaimScore(previousClaim)}")
        print(_SEP + "\n")

        while True:
            raw = input(f"  {rollerName} sanoo: ").strip()
            if raw.lower() == "quit":
                return None
            claimed = _parseClaim(raw)
            if claimed is None:
                print("  Virheellinen syöte. Esim: '43', '55', '21' tai 'mexico'")
                continue
            if previousClaim is not None:
                if previousClaim == 1000 and claimed != 1000:
                    print("  Mexico väitetty — voi sanoa vain 'mexico'")
                    continue
                if previousClaim != 1000 and claimed <= previousClaim:
                    print(f"  Pitää sanoa enemmän kuin {_displayClaimScore(previousClaim)}")
                    continue
            return claimed

    def _showChallengeResult(
        self,
        rollerName: str,
        challengerName: str,
        claimed: int,
        actual: int,
        d1: int,
        d2: int,
        loserName: str,
        drinks: int,
    ) -> None:
        self._clearScreen()
        claimedStr = _displayClaimScore(claimed)
        actualStr = _displayScore(d1, d2)
        rollerLied = actual < claimed
        print("\n" + _SEP)
        if rollerLied:
            print(f"  {rollerName} valehteli!")
        else:
            print(f"  {challengerName} oli väärässä!")
        print()
        print(f"  Väitetty:  {claimedStr}")
        print(f"  Todellinen: {actualStr}")
        print()
        print(f"  {loserName.upper()} JUO {drinks}")
        print(_SEP)

    def _getChallengeDecision(self, rollerName: str, challengerName: str, claimed: int) -> str:
        print("\n" + _SEP)
        print(f"  {rollerName} väitti: {_displayClaimScore(claimed)}")
        print()
        print(f"  {challengerName.upper()}: haasta vai hyväksy?")
        print()
        print("  c = haasta | Enter = hyväksy")
        print(_SEP + "\n")
        return input("  Päätös: ").strip().lower()
