from core.game import Game
from core.deck import Deck
from core.player import Player
from dataclasses import dataclass, field
from core.cards import Cards


def defaultInput(prompt: str) -> str:
    answer = input(prompt).strip().lower()
    if answer == "q":
        print("Quitting...")
        exit()
    return answer


@dataclass
class Buja(Game):
    name: str = "Buja"
    config: dict = field(default_factory=dict)
    deck: Deck = field(default_factory=Deck)

    def __post_init__(self):
        self._input = defaultInput

    def setInput(self, fn):
        self._input = fn

    def playRound(self) -> None:
        print("Red or Black?")

        for player in self.players:
            print(f"\n{player.getName()} turn")
            self._redOrBlack(player)

        print("Higher or Lower")

        for player in self.players:
            print(f"\n{player.getName()} turn")
            self._higherOrLower(player)

        print("Inside or Outside")

        for player in self.players:
            print(f"\n{player.getName()} turn")
            self._insideOrOutside(player)

        print("Which suit?")

        for player in self.players:
            print(f"\n{player.getName()} turn")
            self._suit(player)

        print("\nHands for each player:\n")
        for player in self.players:
            hand_str = ", ".join(str(c) for c in player.getHand())
            print(f"{player.getName()}: {hand_str}")

        print("Next the board phase")

        self._board()

        print("\nDrink tally:\n")
        for player in self.players:
            print(f"{player.getName()}: drank {player.getDrinksTaken()} | gave out {player.drinksToGive}")

    def _redOrBlack(self, player: Player) -> None:
        amount = self._getConfig("drinkAmount", 1)

        guess = ""
        while guess not in ("r", "b"):
            guess = self._input("Red or Black? (r/b) ")

        card = self._draw(player)
        print(f"Card: {card}")

        correct = (guess == "r" and card.isRed()) or (guess == "b" and card.isBlack())

        if correct:
            target = self._chooseTarget(player)
            target.addDrinks(amount)
            player.addDrinksToGive(amount)
        else:
            player.addDrinks(amount)

    def _higherOrLower(self, player: Player) -> None:
        amount = self._getConfig("drinkAmount", 1)

        last = player.getHand()[-1]
        print(f"Your last card: {last}")

        guess = ""
        while guess not in ("h", "l"):
            guess = self._input("Higher or Lower? (h/l) ")

        card = self._draw(player)
        print(f"Drawn card: {card}")

        if card.value() == last.value():
            player.addDrinks(amount * 2)
            return

        correct = (guess == "h" and card.value() > last.value()) or \
                  (guess == "l" and card.value() < last.value())

        if correct:
            target = self._chooseTarget(player)
            target.addDrinks(amount)
            player.addDrinksToGive(amount)
        else:
            player.addDrinks(amount)

    def _insideOrOutside(self, player: Player) -> None:
        amount = self._getConfig("drinkAmount", 1)

        hand = player.getHand()
        low = min(hand, key=lambda c: c.value())
        high = max(hand, key=lambda c: c.value())

        guess = ""
        while guess not in ("i", "o"):
            guess = self._input("Inside or Outside? (i/o) ")

        card = self._draw(player)
        v = card.value()

        on_line = v == low.value() or v == high.value()

        if on_line:
            player.addDrinks(amount * 2)
            return

        correct = (guess == "i" and low.value() < v < high.value()) or \
                  (guess == "o" and (v < low.value() or v > high.value()))

        if correct:
            target = self._chooseTarget(player)
            target.addDrinks(amount)
            player.addDrinksToGive(amount)
        else:
            player.addDrinks(amount)

    def _suit(self, player: Player) -> None:
        amount = self._getConfig("drinkAmount", 1)

        SUIT_MAP = {"h": "hearts", "d": "diamonds", "c": "clubs", "s": "spades"}

        guess = ""
        while guess not in SUIT_MAP:
            guess = self._input("Guess suit (h/d/c/s): ")

        card = self._draw(player)

        if SUIT_MAP[guess] == card.suit.lower():
            target = self._chooseTarget(player)
            target.addDrinks(amount)
            player.addDrinksToGive(amount)
        else:
            player.addDrinks(amount)

    def _board(self) -> None:
        board_length = self._getConfig("boardLength", 3)
        start_drinks = self._getConfig("boardStartDrinks", 2)
        increment = self._getConfig("boardIncrement", 2)

        board = []
        for _ in range(board_length):
            row = [self.deck.drawCard() for _ in range(3)]
            board.append(row)

        for rowIndex, row in enumerate(board):
            drinks = start_drinks + rowIndex * increment

            for cardIndex, card in enumerate(row):
                self._input(f"Press Enter ({card})")

                matched = [p for p in self.players if p.hasRank(card.rank)]

                for player in matched:
                    player.addDrinks(drinks)

    def _chooseTarget(self, player: Player) -> Player:
        others = self._listPlayers(player)

        while True:
            name = self._input("Target player: ")
            target = next((p for p in others if p.getName().lower() == name.lower()), None)
            if target:
                return target

    def _draw(self, player: Player):
        card = self.deck.drawCard()
        player.addCardToHand(card)
        return card

    def _listPlayers(self, exclude: Player):
        return [p for p in self.players if p.getId() != exclude.getId()]

    def _getConfig(self, key, default):
        return self.config.get(key, default)