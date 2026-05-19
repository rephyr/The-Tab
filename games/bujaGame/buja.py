"""
Buja, a card-based drinking game with 4 guess phases followed by a board phase.
Works almost like ride the bus
"""
from core.game import Game
from core.deck import Deck
from core.player import Player
from core.events import (
    GameStartEvent, PhaseEvent, GuessEvent,
    DrinkEvent, GiveEvent, ShareEvent,
    BoardCardEvent, BoardCardDoneEvent, GameEndEvent,
)
from dataclasses import dataclass, field


def defaultInput(prompt: str) -> str:
    answer = input(prompt).strip().lower()
    if answer == "q":
        print("Quitting...")
        exit()
    return answer


@dataclass
class Buja(Game):
    """
    The Buja drinking game. Players go through Red/Black, Higher/Lower,
    Inside/Outside, and Suit phases, then a shared board phase.
    """
    name: str = "Buja instance"
    gameTitle: str = "Buja"

    config: dict = field(default_factory=dict)
    deck: Deck = field(default_factory=Deck)

    def __post_init__(self):
        self.inputFunc = defaultInput
        self.deck.deckCount = self._getConfig("deckCount", 1)

    @staticmethod
    def cardsNeeded(playerCount: int, boardLength: int) -> int:
        """Minimum cards required: 4 phase cards per player + 3 per board row + 1 final card."""
        return 4 * playerCount + boardLength * 3 + 1

    def setInput(self, fn):
        self.inputFunc = fn

    def playRound(self) -> None:
        """Run a full game: all 4 phases for every player, then the board."""
        self.emit(GameStartEvent([p.getName() for p in self.players]))

        print("Red or Black?")
        for player in self.players:
            print(f"\n{player.getName()}'s turn")
            self.emit(PhaseEvent("Red or Black", player.getName()))
            self._redOrBlack(player)

        print("\nHigher or Lower\n")
        for player in self.players:
            print(f"\n{player.getName()}'s turn")
            self.emit(PhaseEvent("Higher or Lower", player.getName()))
            self._higherOrLower(player)

        print("\nInside or Outside\n")
        for player in self.players:
            print(f"\n{player.getName()}'s turn")
            self.emit(PhaseEvent("Inside or Outside", player.getName()))
            self._insideOrOutside(player)

        print("\nWhich suit?\n")
        for player in self.players:
            print(f"\n{player.getName()}'s turn")
            self.emit(PhaseEvent("Suit", player.getName()))
            self._suit(player)

        print("\nHands for each player:\n")
        for player in self.players:
            handStr = ", ".join(str(c) for c in player.getHand())
            print(f"{player.getName()}: {handStr}")

        print("\nNext the board phase\n")
        self.emit(PhaseEvent("Board", ""))
        self._board()

        print("\nDrink tally:\n")
        for player in self.players:
            print(f"{player.getName()}: drank {player.getDrinksTaken()} | gave out {player.drinksToGive}")

        self.emit(GameEndEvent([
            {"name": p.getName(), "drinksTaken": p.getDrinksTaken(), "drinksToGive": p.drinksToGive}
            for p in self.players
        ]))

    def _redOrBlack(self, player: Player) -> None:
        amount = self._getConfig("drinkAmount", 1)

        guess = ""
        while guess not in ("r", "b"):
            guess = self.inputFunc("Red or Black? (r/b) ")

        card = self._draw(player)
        print(f"Card: {card}")

        correct = (guess == "r" and card.isRed()) or (guess == "b" and card.isBlack())
        self.emit(GuessEvent(player.getName(), "Red or Black", "Red" if guess == "r" else "Black", str(card), correct))

        if correct:
            print("Correct!")
            target = self._chooseTarget(player)
            print(f"{target.getName()} drinks {amount}")
            target.addDrinks(amount)
            player.addDrinksToGive(amount)
            self.emit(GiveEvent(player.getName(), target.getName(), amount))
        else:
            print(f"Wrong! You drink {amount}")
            player.addDrinks(amount)
            self.emit(DrinkEvent(player.getName(), amount, "wrong guess"))

    def _higherOrLower(self, player: Player) -> None:
        amount = self._getConfig("drinkAmount", 1)

        lastCard = player.getHand()[-1]
        print(f"Your last card: {lastCard}")

        guess = ""
        while guess not in ("h", "l"):
            guess = self.inputFunc("Higher or Lower? (h/l) ")

        card = self._draw(player)
        print(f"Drawn card: {card}")

        if card.value() == lastCard.value():
            print("Same value! Drink double")
            player.addDrinks(amount * 2)
            self.emit(GuessEvent(player.getName(), "Higher or Lower", None, str(card), None))
            self.emit(DrinkEvent(player.getName(), amount * 2, "same value"))
            return

        correct = (guess == "h" and card.value() > lastCard.value()) or \
                  (guess == "l" and card.value() < lastCard.value())
        self.emit(GuessEvent(player.getName(), "Higher or Lower", "Higher" if guess == "h" else "Lower", str(card), correct))

        if correct:
            print("Correct!")
            target = self._chooseTarget(player)
            print(f"{target.getName()} drinks {amount}")
            target.addDrinks(amount)
            player.addDrinksToGive(amount)
            self.emit(GiveEvent(player.getName(), target.getName(), amount))
        else:
            print(f"Wrong! You drink {amount}")
            player.addDrinks(amount)
            self.emit(DrinkEvent(player.getName(), amount, "wrong guess"))

    def _insideOrOutside(self, player: Player) -> None:
        amount = self._getConfig("drinkAmount", 1)

        hand = player.getHand()

        print(f"\n{player.getName()}'s cards:")
        print(", ".join(str(c) for c in hand))

        low = min(hand, key=lambda c: c.value())
        high = max(hand, key=lambda c: c.value())

        print(f"Range: {low} - {high}")

        guess = ""
        while guess not in ("i", "o"):
            guess = self.inputFunc("Inside or Outside? (i/o) ")

        card = self._draw(player)
        print(f"Card: {card}")

        value = card.value()

        if value == low.value() or value == high.value():
            print(f"On the line! Drink {amount * 2}")
            player.addDrinks(amount * 2)
            self.emit(GuessEvent(player.getName(), "Inside or Outside", None, str(card), None))
            self.emit(DrinkEvent(player.getName(), amount * 2, "on the line"))
            return

        correct = (guess == "i" and low.value() < value < high.value()) or \
                  (guess == "o" and (value < low.value() or value > high.value()))
        self.emit(GuessEvent(player.getName(), "Inside or Outside", "Inside" if guess == "i" else "Outside", str(card), correct))

        if correct:
            print("Correct!")
            target = self._chooseTarget(player)
            print(f"{target.getName()} drinks {amount}")
            target.addDrinks(amount)
            player.addDrinksToGive(amount)
            self.emit(GiveEvent(player.getName(), target.getName(), amount))
        else:
            print(f"Wrong! You drink {amount}")
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

        guess = ""
        while guess not in suitMap:
            guess = self.inputFunc("Guess suit (h/d/c/s): ")

        card = self._draw(player)
        print(f"Card: {card}")

        guessedSuit = suitMap[guess]
        actualSuit = card.suit.lower()
        correct = guessedSuit == actualSuit
        self.emit(GuessEvent(player.getName(), "Suit", guessedSuit.capitalize(), str(card), correct))

        if correct:
            print("Correct!")
            target = self._chooseTarget(player)
            print(f"{target.getName()} drinks {amount}")
            target.addDrinks(amount)
            player.addDrinksToGive(amount)
            self.emit(GiveEvent(player.getName(), target.getName(), amount))
        else:
            print(f"Wrong! You drink {amount}")
            player.addDrinks(amount)
            self.emit(DrinkEvent(player.getName(), amount, "wrong guess"))

    def _board(self) -> None:
        boardLength = self._getConfig("boardLength", 3)
        startDrinks = self._getConfig("boardStartDrinks", 2)
        increment = self._getConfig("boardIncrement", 2)

        actions = ["drink", "give", "share"]

        board = []
        for _ in range(boardLength):
            row = [self.deck.drawCard() for _ in range(3)]
            board.append(row)

        finalCard = self.deck.drawCard()
        lastRowDrinks = startDrinks + (boardLength - 1) * increment
        finalDrinks = lastRowDrinks * 2

        if self._getConfig("debug", False):
            print("\n=== THE BOARD (DEBUG PREVIEW) ===\n")
            for rowIndex, row in enumerate(board):
                drinks = startDrinks + rowIndex * increment
                rowPreview = []
                for cardIndex, card in enumerate(row):
                    action = actions[cardIndex % len(actions)]
                    rowPreview.append(f"{card} ({action.upper()})")
                print(f"Row {rowIndex + 1} | {drinks} drinks | " + " | ".join(rowPreview))
            print(f"Final  | {finalDrinks} drinks | {finalCard} (SHARE)")

        print("\n=== BOARD PHASE START ===\n")

        for rowIndex, row in enumerate(board):
            drinks = startDrinks + rowIndex * increment

            print(f"\nRow {rowIndex + 1} | {drinks} drinks")

            for cardIndex, card in enumerate(row):
                action = actions[cardIndex % len(actions)]

                input(f"\nPress Enter to reveal ({card} - {action.upper()})")

                print(f"Card: {card} | Action: {action.upper()}")

                matchedPlayers = [p for p in self.players if p.hasRank(card.rank)]
                self.emit(BoardCardEvent(str(card), action, drinks, [p.getName() for p in matchedPlayers]))

                if not matchedPlayers:
                    print("Nobody matched this card.")
                else:
                    for player in matchedPlayers:
                        if action == "drink":
                            print(f"{player.getName()} drinks {drinks}")
                            player.addDrinks(drinks)
                            self.emit(DrinkEvent(player.getName(), drinks, "board"))

                        elif action == "give":
                            target = self._chooseTarget(player)
                            print(f"{target.getName()} gets {drinks}")
                            target.addDrinks(drinks)
                            player.addDrinksToGive(drinks)
                            self.emit(GiveEvent(player.getName(), target.getName(), drinks))

                        elif action == "share":
                            target = self._chooseTarget(player)
                            print(f"{player.getName()} and {target.getName()} share {drinks}")
                            player.addDrinks(drinks)
                            target.addDrinks(drinks)
                            player.addDrinksToGive(drinks)
                            self.emit(ShareEvent(player.getName(), target.getName(), drinks))

                self.emit(BoardCardDoneEvent())

        print(f"\n=== FINAL CARD | {finalDrinks} drinks | SHARE ===")
        input(f"\nPress Enter to reveal")
        print(f"Card: {finalCard} | Action: SHARE")

        matchedPlayers = [p for p in self.players if p.hasRank(finalCard.rank)]
        self.emit(BoardCardEvent(str(finalCard), "share", finalDrinks, [p.getName() for p in matchedPlayers]))

        if not matchedPlayers:
            print("Nobody matched this card.")
        else:
            for player in matchedPlayers:
                target = self._chooseTarget(player)
                print(f"{player.getName()} and {target.getName()} share {finalDrinks}")
                player.addDrinks(finalDrinks)
                target.addDrinks(finalDrinks)
                player.addDrinksToGive(finalDrinks)
                self.emit(ShareEvent(player.getName(), target.getName(), finalDrinks))

        self.emit(BoardCardDoneEvent())

        print("\n=== BOARD END ===\n")

    def _chooseTarget(self, player: Player) -> Player:
        others = self._listPlayers(player)

        print("\nAvailable players:")
        for p in others:
            print(f"- {p.getName()}")

        while True:
            name = self.inputFunc("Target player: ").strip()

            target = next(
                (p for p in others if p.getName().lower() == name.lower()),
                None
            )

            if target:
                return target

            print("Invalid name, try again")

    def _draw(self, player: Player):
        card = self.deck.drawCard()

        if card is None:
            self.deck.resetDeck()
            card = self.deck.drawCard()

        player.addCardToHand(card)
        return card

    def _listPlayers(self, exclude: Player):
        return [p for p in self.players if p.getId() != exclude.getId()]

    def _getConfig(self, key, default):
        return self.config.get(key, default)

    def _handleGive(self, player: Player, drinks: int) -> None:
        target = self._chooseTarget(player)
        print(f"{target.getName()} gets {drinks}")
        target.addDrinks(drinks)
        player.addDrinksToGive(drinks)

    def _handleShare(self, player: Player, drinks: int) -> None:
        target = self._chooseTarget(player)
        print(f"{player.getName()} and {target.getName()} share {drinks}")
        player.addDrinks(drinks)
        target.addDrinks(drinks)
        player.addDrinksToGive(drinks)
