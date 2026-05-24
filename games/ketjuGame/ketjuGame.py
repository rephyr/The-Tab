"""
Ketju — a higher/lower streak card game with escalating stakes.

One player draws cards until their turn ends (wrong guess, equal card,
voluntary exit, or Double or Double). The previous player is always
chained — they mirror-drink whenever the current player drinks.
The chain passes to the new previous player after each turn.
"""
from dataclasses import dataclass, field
from typing import Optional, Tuple

from core.game import Game
from core.deck import Deck
from core.cards import Card
from core.events import GameStartEvent, GameEndEvent, DrinkEvent
from games.ketjuGame.ketjuEvents import (
    KetjuCardDrawnEvent, KetjuEqualCardEvent, KetjuDoubleOrDoubleEvent,
    KetjuExitEvent, KetjuLinkResolvedEvent,
)

_POT = {0: 1, 1: 1, 2: 2, 3: 3, 4: 5, 5: 10}
_COMPLEX_HEART = "❤︎⁠"
_SEP = "=" * 32
_DIV = "-" * 32


def _pot(streak: int) -> int:
    return _POT.get(streak, _POT[max(_POT)])


def _printCard(card) -> str:
    """Printer-safe card string — replaces complex ❤︎⁠ with ♥."""
    return str(card).replace(_COMPLEX_HEART, "♥")


@dataclass
class KetjuGame(Game):
    gameTitle: str = "Ketju"
    config: dict = field(default_factory=dict)

    def playRound(self) -> None:
        cfg = self.config.get("ketju", {})
        deckCount = int(cfg.get("deckCount", 1))
        minStreakToExit = int(cfg.get("minStreakToExit", 3))
        finalThreshold = int(cfg.get("finalThreshold", 5))
        multiplierCap = int(cfg.get("multiplierCap", 8))
        equalPenalty = int(cfg.get("equalPenalty", 3))

        deck = Deck(deckCount=deckCount)
        deck.resetDeck()
        self.emit(GameStartEvent([p.getName() for p in self.players]))

        # Draw the starting card — no turn owner, just sets the first prevCard
        prevCard: Card = deck.drawCard()
        self._clearScreen()
        print(f"\n{_SEP}")
        print("  KETJU")
        print(f"\n  Aloituskortti: {prevCard}")
        print(f"\n{_SEP}")
        input("")

        playerIndex = 0
        multiplier = 1
        chainedPlayer: Optional[str] = None

        try:
            while True:
                player = self.players[playerIndex % len(self.players)]

                result = self._runPlayerTurn(
                    player, prevCard, multiplier, chainedPlayer,
                    minStreakToExit, finalThreshold, multiplierCap, equalPenalty, deck,
                )
                if result is None:
                    break
                prevCard, multiplier = result

                # Every player becomes chained after their turn — only 1 chain at a time
                chainedPlayer = player.getName()
                playerIndex += 1

        except KeyboardInterrupt:
            print()

        self.emit(GameEndEvent([
            {"name": p.getName(), "drinksTaken": p.getDrinksTaken(), "drinksToGive": p.drinksToGive}
            for p in self.players
        ]))

    def _runPlayerTurn(
        self,
        player,
        prevCard: Card,
        multiplier: int,
        chainedPlayer: Optional[str],
        minStreakToExit: int,
        finalThreshold: int,
        multiplierCap: int,
        equalPenalty: int,
        deck: Deck,
    ) -> Optional[Tuple[Card, int]]:
        """
        Run one player's full turn until it ends.
        Returns (newPrevCard, newMultiplier) or None if quit.
        The player guesses BEFORE the card is drawn.
        """
        streak = 0

        while True:
            self._clearScreen()
            self._showTurnPrompt(player.getName(), prevCard, streak, multiplier, chainedPlayer)

            # Guess BEFORE drawing
            while True:
                raw = input(f"  {player.getName()}: ").strip().lower()
                if raw == "quit":
                    return None
                if raw in ("h", "l"):
                    break
                print("  h = higher, l = lower")

            guess = raw
            guessWord = "korkeampi" if guess == "h" else "matalampi"

            if deck.cardsRemaining() == 0:
                deck.resetDeck()
            card = deck.drawCard()
            self._clearScreen()

            # Equal card
            if card.value() == prevCard.value():
                total = equalPenalty * multiplier
                player.addDrinks(total)
                self.emit(KetjuEqualCardEvent(
                    player=player.getName(), card=_printCard(card), previousCard=_printCard(prevCard),
                    penalty=equalPenalty, multiplier=multiplier, total=total,
                ))
                self.emit(DrinkEvent(player.getName(), total, "ketju-tasakortti"))
                self._mirrorChain(chainedPlayer, player.getName(), total)
                print(f"\n{_SEP}")
                print(f"  Nostettu: {card}")
                print(f"  Aiempi:   {prevCard}")
                print(_DIV)
                print(f"  SAMA KORTTI!  {player.getName()} juo {total}!")
                if chainedPlayer and chainedPlayer != player.getName():
                    print(f"  KETJU:        {chainedPlayer} juo {total}!")
                print(_SEP)
                input("")
                return (card, 1)

            actualHigher = card.value() > prevCard.value()
            correct = (guess == "h" and actualHigher) or (guess == "l" and not actualHigher)

            if not correct:
                drinks = _pot(streak) * multiplier
                player.addDrinks(drinks)
                self.emit(KetjuCardDrawnEvent(
                    player=player.getName(), card=_printCard(card), previousCard=_printCard(prevCard),
                    guess=guessWord, correct=False, streak=streak,
                    pot=_pot(streak), multiplier=multiplier,
                ))
                self.emit(DrinkEvent(player.getName(), drinks, "ketju-väärä"))
                self._mirrorChain(chainedPlayer, player.getName(), drinks)
                print(f"\n{_SEP}")
                print(f"  Nostettu: {card}  ({guessWord})")
                print(f"  Aiempi:   {prevCard}")
                print(_DIV)
                print(f"  VÄÄRIN!  {player.getName()} juo {drinks}!")
                if chainedPlayer and chainedPlayer != player.getName():
                    print(f"  KETJU:   {chainedPlayer} juo {drinks}!")
                print(_SEP)
                input("")
                return (card, 1)

            # Correct guess
            streak += 1
            self.emit(KetjuCardDrawnEvent(
                player=player.getName(), card=_printCard(card), previousCard=_printCard(prevCard),
                guess=guessWord, correct=True, streak=streak,
                pot=_pot(streak), multiplier=multiplier,
            ))
            oldPrevCard = prevCard
            prevCard = card

            if streak >= finalThreshold:
                # Offer tap-out before Double or Double
                self._clearScreen()
                print(f"\n{_SEP}")
                print(f"  Nostettu: {card}  ({guessWord})")
                print(f"  Aiempi:   {oldPrevCard}")
                print(_DIV)
                print(f"  OIKEIN!  Putki: {streak}  —  DOUBLE OR DOUBLE!")
                if multiplier > 1:
                    print(f"  Kerroin: ×{multiplier}")
                print()
                print("  e = poistu (ketjutetaan)  |  Enter = Double or Double")
                print('  (tai "quit")')
                print(_SEP)
                raw = input(f"  {player.getName()}: ").strip().lower()
                if raw == "quit":
                    return None
                if raw == "e":
                    giveAmount = _pot(finalThreshold)
                    self.emit(KetjuExitEvent(player.getName(), giveAmount, streak))
                    player.pendingGive = giveAmount
                    self._interactiveGivePhase()
                    return (prevCard, 1)
                result = self._doDoubleOrDouble(
                    player, prevCard, multiplier, finalThreshold, multiplierCap, deck, chainedPlayer,
                )
                if result is None:
                    return None
                return result

            if streak >= minStreakToExit:
                # Show result + offer exit on the same screen
                self._clearScreen()
                print(f"\n{_SEP}")
                print(f"  Nostettu: {card}  ({guessWord})")
                print(f"  Aiempi:   {oldPrevCard}")
                print(_DIV)
                print(f"  OIKEIN!  Putki: {streak}  |  Panos: {_pot(streak)} juo.")
                if multiplier > 1:
                    print(f"  Kerroin: ×{multiplier}")
                print()
                print("  e = poistu (ketjutetaan)  |  Enter = jatka")
                print('  (tai "quit")')
                print(_SEP)
                raw = input(f"  {player.getName()}: ").strip().lower()
                if raw == "quit":
                    return None
                if raw == "e":
                    giveAmount = _pot(streak)
                    self.emit(KetjuExitEvent(player.getName(), giveAmount, streak))
                    player.pendingGive = giveAmount
                    self._interactiveGivePhase()
                    return (prevCard, 1)
                # Continue
                continue

            # Below exit threshold — show result and continue automatically
            print(f"\n{_SEP}")
            print(f"  Nostettu: {card}  ({guessWord})")
            print(f"  Aiempi:   {oldPrevCard}")
            print(_DIV)
            print(f"  OIKEIN!  Putki: {streak}  |  Panos: {_pot(streak)} juo.")
            if multiplier > 1:
                print(f"  Kerroin: ×{multiplier}")
            print(_SEP)
            input("")

    def _mirrorChain(self, chainedPlayer: Optional[str], triggerPlayer: str, amount: int) -> None:
        """Chained player mirror-drinks when trigger player drinks."""
        if chainedPlayer and chainedPlayer != triggerPlayer and amount > 0:
            linked = next((p for p in self.players if p.getName() == chainedPlayer), None)
            if linked:
                linked.addDrinks(amount)
                self.emit(KetjuLinkResolvedEvent(chainedPlayer, triggerPlayer, amount))
                self.emit(DrinkEvent(chainedPlayer, amount, "ketju-linkki"))

    def _showTurnPrompt(
        self, playerName: str, prevCard: Card, streak: int, multiplier: int, chainedPlayer: Optional[str]
    ) -> None:
        chainStr = chainedPlayer if chainedPlayer else "-"
        print(f"\n{_SEP}")
        print(f"  Nykyinen:   {prevCard}")
        print(f"  Putki:      {streak}  |  Panos: {_pot(streak)} juo.")
        if multiplier > 1:
            print(f"  Kerroin:    ×{multiplier}")
        print(f"  Ketjutettu: {chainStr}")
        print(_DIV)
        print(f"  >>> {playerName.upper()} ARVAA <<<")
        print()
        print("  h = higher  |  l = lower")
        print('  (tai "quit")')
        print(_SEP)

    def _doDoubleOrDouble(
        self,
        player,
        prevCard: Card,
        multiplier: int,
        finalThreshold: int,
        multiplierCap: int,
        deck: Deck,
        chainedPlayer: Optional[str],
    ) -> Optional[Tuple[Card, int]]:
        """Double or Double sub-game. Returns (newPrevCard, newMultiplier) or None (quit)."""
        # Step 1: show current card + ask for guess (challenge card still hidden)
        self._clearScreen()
        print(f"\n{_SEP}")
        print("  DOUBLE OR DOUBLE!")
        print(f"  Putki {finalThreshold} täynnä!")
        print(_DIV)
        print(f"  Nykyinen kortti: {prevCard}")
        print(f"  Panos: {_pot(finalThreshold)} juo.  |  Kerroin: ×{multiplier}")
        print()
        print("  h = higher  |  l = lower")
        print('  (tai "quit")')
        print(_SEP)
        while True:
            raw = input(f"  {player.getName()}: ").strip().lower()
            if raw == "quit":
                return None
            if raw in ("h", "l"):
                break
            print("  Virheellinen. h = higher, l = lower")

        # Step 2: draw challenge card AFTER guess
        if deck.cardsRemaining() == 0:
            deck.resetDeck()
        challengeCard = deck.drawCard()

        guessWord = "korkeampi" if raw == "h" else "matalampi"
        actualHigher = challengeCard.value() > prevCard.value()
        correct = (raw == "h" and actualHigher) or (raw == "l" and not actualHigher)

        # Step 3: reveal result
        self._clearScreen()
        if correct:
            newMult = min(multiplier * 2, multiplierCap)
            payout = _pot(finalThreshold) * newMult
            self.emit(KetjuDoubleOrDoubleEvent(
                player=player.getName(), challengeCard=_printCard(challengeCard),
                previousCard=_printCard(prevCard), guess=guessWord, correct=True,
                pot=_pot(finalThreshold), multiplier=multiplier, amount=payout,
            ))
            returnMult = 1 if newMult >= multiplierCap else newMult
            print(f"\n{_SEP}")
            print(f"  Nykyinen: {prevCard}")
            print(f"  Haaste:   {challengeCard}  ({guessWord})")
            print(_DIV)
            print(f"  OIKEIN!  {player.getName()} jakaa {payout} juomaa!")
            print(f"  Kerroin seuraavalle: ×{returnMult}")
            print(_SEP)
            player.pendingGive = payout
            self._interactiveGivePhase()
            input("")
            return (challengeCard, returnMult)
        else:
            drinks = _pot(finalThreshold) * 2
            player.addDrinks(drinks)
            self.emit(KetjuDoubleOrDoubleEvent(
                player=player.getName(), challengeCard=_printCard(challengeCard),
                previousCard=_printCard(prevCard), guess=guessWord, correct=False,
                pot=_pot(finalThreshold), multiplier=multiplier, amount=drinks,
            ))
            self.emit(DrinkEvent(player.getName(), drinks, "ketju-double"))
            self._mirrorChain(chainedPlayer, player.getName(), drinks)
            print(f"\n{_SEP}")
            print(f"  Nykyinen: {prevCard}")
            print(f"  Haaste:   {challengeCard}  ({guessWord})")
            print(_DIV)
            print(f"  VÄÄRIN!  {player.getName()} juo {drinks}!")
            if chainedPlayer and chainedPlayer != player.getName():
                print(f"  KETJU:   {chainedPlayer} juo {drinks}!")
            print(_SEP)
            input("\n  Paina Enter jatkaaksesi...")
            return (challengeCard, 1)
