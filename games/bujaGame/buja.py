"""
Buja, a card-based drinking game with 4 guess phases followed by a board phase.
Works almost like ride the bus
"""
from core.game import Game
from core.deck import Deck
from core.player import Player
from core.events import (
    GameStartEvent, PhaseEvent, GuessEvent,
    DrinkEvent, ShareEvent,
    BoardCardEvent, BoardCardDoneEvent, GameEndEvent,
)
from dataclasses import dataclass, field


def _defaultInput(prompt: str) -> str:
    answer = input(prompt).strip().lower()
    if answer == "quit":
        print("Lopetetaan...")
        exit()
    return answer


@dataclass
class Buja(Game):
    """
    The Buja drinking game. Players go through Red/Black, Higher/Lower,
    Inside/Outside, and Suit phases, then a shared board phase.
    """
    gameTitle: str = "Buja"

    config: dict = field(default_factory=dict)
    deck: Deck = field(default_factory=Deck)

    def __post_init__(self):
        self.inputFunc = _defaultInput
        self.deck.deckCount = self._getConfig("deckCount", 1)
        self.deck.resetDeck()

    @staticmethod
    def cardsNeeded(playerCount: int, boardLength: int) -> int:
        """Minimum cards required: 4 phase cards per player + 3 per board row + 1 final card."""
        return 4 * playerCount + boardLength * 3 + 1

    def _setInput(self, fn):
        self.inputFunc = fn

    def playRound(self) -> None:
        """Run a full game: all 4 phases for every player, then the board."""
        self.emit(GameStartEvent([p.getName() for p in self.players]))

        print("Mikä maa?")
        for player in self.players:
            print(f"\n{player.getName()}n vuoro")
            self.emit(PhaseEvent("Mikä maa?", player.getName()))
            self._redOrBlack(player)

        print("\nIsompi vai pienempi?\n")
        for player in self.players:
            print(f"\n{player.getName()}n vuoro")
            self.emit(PhaseEvent("Isompi vai pienempi?", player.getName()))
            self._higherOrLower(player)

        print("\nVälistä vai ulkoa?\n")
        for player in self.players:
            print(f"\n{player.getName()}n vuoro")
            self.emit(PhaseEvent("Välistä vai ulkoa?", player.getName()))
            self._insideOrOutside(player)

        print("\nMikä maa?\n")
        for player in self.players:
            print(f"\n{player.getName()}n vuoro")
            self.emit(PhaseEvent("Mikä maa?", player.getName()))
            self._suit(player)

        print("\nKädet:\n")
        for player in self.players:
            handStr = ", ".join(str(c) for c in player.getHand())
            print(f"{player.getName()}: {handStr}")

        print("\nSeuraavana lauta!\n")
        self.emit(PhaseEvent("Lauta", ""))
        self._board()

        self._interactiveGivePhase()

        print("\nRyyppytaulu:\n")
        for player in self.players:
            print(f"{player.getName()}: joi {player.getDrinksTaken()} | antoi {player.drinksToGive}")

        self.emit(GameEndEvent([
            {"name": p.getName(), "drinksTaken": p.getDrinksTaken(), "drinksToGive": p.drinksToGive}
            for p in self.players
        ]))

    def _redOrBlack(self, player: Player) -> None:
        amount = self._getConfig("drinkAmount", 1)

        guess = ""
        while guess not in ("r", "b"):
            guess = self.inputFunc("Punainen (r) vai musta (b)? ")

        card = self._draw(player)
        print(f"Kortti: {card}")

        correct = (guess == "r" and card.isRed()) or (guess == "b" and card.isBlack())
        self.emit(GuessEvent(player.getName(), "Mikä maa?", "Punainen" if guess == "r" else "Musta", str(card), correct))

        if correct:
            print("Oikein!")
            player.pendingGive += amount
        else:
            print(f"Väärin! Juo {amount}")
            player.addDrinks(amount)
            self.emit(DrinkEvent(player.getName(), amount, "wrong guess"))

    def _higherOrLower(self, player: Player) -> None:
        amount = self._getConfig("drinkAmount", 1)

        lastCard = player.getHand()[-1]
        print(f"Viime kortti: {lastCard}")

        guess = ""
        while guess not in ("h", "l"):
            guess = self.inputFunc("Isompi (h) vai pienempi (l)? ")

        card = self._draw(player)
        print(f"Kortti: {card}")

        if card.value() == lastCard.value():
            print("Sama arvo! Juo tupla")
            player.addDrinks(amount * 2)
            self.emit(GuessEvent(player.getName(), "Isompi vai pienempi?", None, str(card), None))
            self.emit(DrinkEvent(player.getName(), amount * 2, "sama arvo"))
            return

        correct = (guess == "h" and card.value() > lastCard.value()) or \
                  (guess == "l" and card.value() < lastCard.value())
        self.emit(GuessEvent(player.getName(), "Isompi vai pienempi?", "Isompi" if guess == "h" else "Pienempi", str(card), correct))

        if correct:
            print("Oikein!")
            player.pendingGive += amount
        else:
            print(f"Väärin! Juo {amount}")
            player.addDrinks(amount)
            self.emit(DrinkEvent(player.getName(), amount, "wrong guess"))

    def _insideOrOutside(self, player: Player) -> None:
        amount = self._getConfig("drinkAmount", 1)

        hand = player.getHand()

        print(f"\n{player.getName()}n kortit:")
        print(", ".join(str(c) for c in hand))

        low = min(hand, key=lambda c: c.value())
        high = max(hand, key=lambda c: c.value())

        print(f"Väli: {low} - {high}")

        guess = ""
        while guess not in ("i", "o"):
            guess = self.inputFunc("Välistä (i) vai ulkoa (o)? ")

        card = self._draw(player)
        print(f"Kortti: {card}")

        value = card.value()

        if value == low.value() or value == high.value():
            print(f"Rajoilla! Juo {amount * 2}")
            player.addDrinks(amount * 2)
            self.emit(GuessEvent(player.getName(), "Välistä vai ulkoa?", None, str(card), None))
            self.emit(DrinkEvent(player.getName(), amount * 2, "rajoilla"))
            return

        correct = (guess == "i" and low.value() < value < high.value()) or \
                  (guess == "o" and (value < low.value() or value > high.value()))
        self.emit(GuessEvent(player.getName(), "Välistä vai ulkoa?", "Välistä" if guess == "i" else "Ulkoa", str(card), correct))

        if correct:
            print("Oikein!")
            player.pendingGive += amount
        else:
            print(f"Väärin! Juo {amount}")
            player.addDrinks(amount)
            self.emit(DrinkEvent(player.getName(), amount, "wrong guess"))

    def _suit(self, player: Player) -> None:
        amount = self._getConfig("drinkAmount", 1)

        suitMap = {
            "h": "hearts",
            "d": "diamonds",
            "c": "clubs",
            "s": "spades"
        }
        suitFi = {"hearts": "Hertta", "diamonds": "Ruutu", "clubs": "Risti", "spades": "Pata"}

        guess = ""
        while guess not in suitMap:
            guess = self.inputFunc("Mikä maa? (h=hertta, d=ruutu, c=risti, s=pata): ")

        card = self._draw(player)
        print(f"Kortti: {card}")

        guessedSuit = suitMap[guess]
        actualSuit = card.suit.lower()
        correct = guessedSuit == actualSuit
        self.emit(GuessEvent(player.getName(), "Mikä maa?", suitFi.get(guessedSuit, guessedSuit.capitalize()), str(card), correct))

        if correct:
            print("Oikein!")
            player.pendingGive += amount
        else:
            print(f"Väärin! Juo {amount}")
            player.addDrinks(amount)
            self.emit(DrinkEvent(player.getName(), amount, "wrong guess"))

    def _board(self) -> None:
        boardLength = self._getConfig("boardLength", 3)
        startDrinks = self._getConfig("boardStartDrinks", 2)
        increment = self._getConfig("boardIncrement", 2)

        actions = ["juo", "jaa", "kippistä"]

        board = []
        for _ in range(boardLength):
            row = [self.deck.drawCard() for _ in range(3)]
            board.append(row)

        finalCard = self.deck.drawCard()
        lastRowDrinks = startDrinks + (boardLength - 1) * increment
        finalDrinks = lastRowDrinks * 2

        if self._getConfig("debug", False):
            print("\n=== LAUTA (ESIKATSELU) ===\n")
            for rowIndex, row in enumerate(board):
                drinks = startDrinks + rowIndex * increment
                rowPreview = []
                for cardIndex, card in enumerate(row):
                    action = actions[cardIndex % len(actions)]
                    rowPreview.append(f"{card} ({action.upper()})")
                print(f"Rivi {rowIndex + 1} | {drinks} ryyppyä | " + " | ".join(rowPreview))
            print(f"Loppu  | {finalDrinks} ryyppyä | {finalCard} (KIPPISTÄ)")

        print("\n=== LAUTA ALKAA ===\n")

        for rowIndex, row in enumerate(board):
            drinks = startDrinks + rowIndex * increment

            print(f"\nRivi {rowIndex + 1} | {drinks} ryyppyä")

            for cardIndex, card in enumerate(row):
                action = actions[cardIndex % len(actions)]

                input(f"\nPaina Enter paljastaaksesi ({card} - {action.upper()})")

                print(f"Kortti: {card} | Toiminto: {action.upper()}")

                matchedPlayers = [p for p in self.players if p.hasRank(card.rank)]
                self.emit(BoardCardEvent(str(card), action, drinks, [p.getName() for p in matchedPlayers]))

                if not matchedPlayers:
                    print("Ei osumia.")
                else:
                    for player in matchedPlayers:
                        if action == "juo":
                            print(f"{player.getName()} juo {drinks}")
                            player.addDrinks(drinks)
                            self.emit(DrinkEvent(player.getName(), drinks, "lauta"))

                        elif action == "jaa":
                            print(f"{player.getName()} antaa {drinks} lopussa")
                            player.pendingGive += drinks

                        elif action == "kippistä":
                            target = self._chooseTarget(player)
                            print(f"{player.getName()} ja {target.getName()} kippistää {drinks}")
                            player.addDrinks(drinks)
                            target.addDrinks(drinks)
                            player.addDrinksToGive(drinks)
                            self.emit(ShareEvent(player.getName(), target.getName(), drinks))

                self.emit(BoardCardDoneEvent())

        print(f"\n=== LOPPU | {finalDrinks} ryyppyä | KIPPISTÄ ===")
        input(f"\nPaina Enter paljastaaksesi")
        print(f"Kortti: {finalCard} | Toiminto: KIPPISTÄ")

        matchedPlayers = [p for p in self.players if p.hasRank(finalCard.rank)]
        self.emit(BoardCardEvent(str(finalCard), "kippistä", finalDrinks, [p.getName() for p in matchedPlayers]))

        if not matchedPlayers:
            print("Ei osumia.")
        else:
            for player in matchedPlayers:
                target = self._chooseTarget(player)
                print(f"{player.getName()} ja {target.getName()} kippistää {finalDrinks}")
                player.addDrinks(finalDrinks)
                target.addDrinks(finalDrinks)
                player.addDrinksToGive(finalDrinks)
                self.emit(ShareEvent(player.getName(), target.getName(), finalDrinks))

        self.emit(BoardCardDoneEvent())

        print("\n=== LAUTA LOPPU ===\n")

    def _chooseTarget(self, player: Player) -> Player:
        others = self._listPlayers(player)

        print("\nPelaajat:")
        for i, p in enumerate(others, 1):
            print(f"  {i}. {p.getName()}")

        while True:
            raw = self.inputFunc("Kenelle? (numero tai nimi): ").strip()
            target = self._findTargetByNameOrNumber(raw, others)
            if target:
                return target
            print("Tuntematon pelaaja, yritä uudelleen")

    def _draw(self, player: Player):
        card = self.deck.drawCard()

        if card is None:
            print("Virhe: kortit loppuivat kesken pelin!")
            while True:
                ans = self.inputFunc("Lisätäänkö yksi pakka? (k/e): ")
                if ans == "k":
                    extra = Deck()
                    extra.buildDeck()
                    extra.shuffleDeck()
                    self.deck.cards.extend(extra.cards)
                    self.deck.deckCount += 1
                    card = self.deck.drawCard()
                    break
                elif ans == "e":
                    print("Peli lopetetaan.")
                    exit()

        player.addCardToHand(card)
        return card

    def _listPlayers(self, exclude: Player):
        return [p for p in self.players if p.getId() != exclude.getId()]

    def _getConfig(self, key, default):
        return self.config.get(key, default)
