from core.game import Game
from core.deck import Deck
from core.player import Player
from dataclasses import dataclass, field
from core.cards import Cards

DRINKAMOUNT = 1
BOARD_LENGTH = 3
BOARD_START = 2
BOARD_INCREMENT = 2
BOARD_DRINKS = 2

SUIT_MAP = {
    "h": "hearts",
    "d": "diamonds",
    "c": "clubs",
    "s": "spades",
}
def _input(prompt: str) -> str:
    answer = input(prompt).strip().lower()
    if answer == "q":
        print("Quitting...")
        exit()
    return answer

@dataclass
class Buja(Game): 
    deck: Deck = field(default_factory=Deck)
    
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
            
        print(f"\nHands for each player:\n")
        for player in self.players:
            hand_str = ", ".join(str(c) for c in player.getHand())
            print(f"{player.getName()}: {hand_str}")
        
        print("Next the board phase")
        
        self._board()

        print(f"\nDrink tally:\n")
        for player in self.players:
            print(f"{player.getName()}: drank {player.getDrinksTaken()} | gave out {player.drinksToGive}")
                   
    def _redOrBlack(self, player: Player) -> None:
            guess = ""

            while guess not in ("r", "b"):
                guess = _input("Red or Black? (r/b)").strip().lower()

            card = self._draw(player)
            print(f"Card: {card}")

            correct = (guess == "r" and card.isRed()) or (guess == "b" and card.isBlack())

            if correct:
                print(f"Correct! Give out {DRINKAMOUNT}")

                target = self._chooseTarget(player)
                target.addDrinks(DRINKAMOUNT)

                player.addDrinksToGive(DRINKAMOUNT)

            else:
                print(f"Wrong: drink {DRINKAMOUNT}")
                player.addDrinks(DRINKAMOUNT)

    def _higherOrLower(self, player: Player) -> None:
        last = player.getHand()[-1]
        print(f"Your last card: {last}")

        guess = ""
        while guess not in ("h", "l"):
            guess = _input("Higher or Lower? (h/l)").strip().lower()

        card = self._draw(player)
        print(f"Drawn card: {card}")

        # same value case (no target needed)
        if card.value() == last.value():
            toDrink = DRINKAMOUNT * 2
            print(f"Same value → you drink {toDrink}")
            player.addDrinks(toDrink)
            return

        correct = (guess == "h" and card.value() > last.value()) or \
                (guess == "l" and card.value() < last.value())

        if correct:
            print(f"Correct!")

            target = self._chooseTarget(player)
            print(f"{target.getName()} gets {DRINKAMOUNT}")

            target.addDrinks(DRINKAMOUNT)
            player.addDrinksToGive(DRINKAMOUNT)

        else:
            print(f"Wrong: drink {DRINKAMOUNT}")
        player.addDrinks(DRINKAMOUNT)
    
    def _insideOrOutside(self, player: Player) -> None:
        hand = player.getHand()

        low = min(hand, key=lambda c: c.value())
        high = max(hand, key=lambda c: c.value())

        print(f"Your cards: {', '.join(str(c) for c in hand)}")
        print(f"Range: {low} - {high}")

        guess = ""
        while guess not in ("i", "o"):
            guess = _input("Inside or Outside? (i/o)").strip().lower()

        card = self._draw(player)
        print(f"Card: {card}")
        v = card.value()

        on_line = (v == low.value() or v == high.value())

        if on_line:
            print(f"On the line → you drink {DRINKAMOUNT * 2}")
            player.addDrinks(DRINKAMOUNT * 2)
            return

        correct = (guess == "i" and low.value() < v < high.value()) or \
                (guess == "o" and (v < low.value() or v > high.value()))

        if correct:
            print(f"Correct!")

            target = self._chooseTarget(player)
            print(f"{target.getName()} gets {DRINKAMOUNT}")

            target.addDrinks(DRINKAMOUNT)
            player.addDrinksToGive(DRINKAMOUNT)

        else:
            print(f"Wrong: drink {DRINKAMOUNT}")
            player.addDrinks(DRINKAMOUNT)
    
    def _suit(self, player: Player) -> None:
        print("Suits: h (Hearts), d (Diamonds), c (Clubs), s (Spades)")

        guess = ""
        while guess not in SUIT_MAP:
            guess = _input("Guess suit (h/d/c/s): ").strip().lower()

        card = self._draw(player)
        print(f"Card: {card}")

        correct = SUIT_MAP[guess] == card.suit.lower()

        if correct:
            print("Correct!")

            target = self._chooseTarget(player)
            print(f"{target.getName()} gets {DRINKAMOUNT}")

            target.addDrinks(DRINKAMOUNT)
            player.addDrinksToGive(DRINKAMOUNT)

        else:
            print(f"Wrong → you drink {DRINKAMOUNT}")
            player.addDrinks(DRINKAMOUNT)

    def _printBoard(self, board: list, start_drinks: int, increment: int) -> None:
        print("\n" + "=" * 50)
        print(f"{'THE BOARD':^50}")
        print("=" * 50)

        actions = ["DRINK", "GIVE", "SHARE"]

        for rowIndex, row in enumerate(board):
            drinks = start_drinks + rowIndex * increment

            row_parts = []

            for cardIndex, card in enumerate(row):
                action = actions[cardIndex]
                row_parts.append(f"{card} ({action})")

            row_str = " | ".join(row_parts)

            print(f"Row {rowIndex + 1} | {drinks} drinks | {row_str}")

        print("=" * 50 + "\n")

    def _board(self) -> None:
        start_drinks = int(_input("Starting drinks for first row: "))
        increment = int(_input("Increment per row: "))

        board = []

        for _ in range(BOARD_LENGTH):
            row = []

            for _ in range(3):
                card = self.deck.drawCard()
                row.append(card)

            board.append(row)

        self._printBoard(board, start_drinks, increment)

        actions = ["drink", "give", "share"]

        for rowIndex, row in enumerate(board):
            drinks = start_drinks + rowIndex * increment

            print(f"\nRow {rowIndex + 1} | {drinks} drinks")

            for cardIndex, card in enumerate(row):
                action = actions[cardIndex]

                input(f"Press Enter to reveal next card ({action.upper()})...")

                print(f"  {card} | {action.upper()}")

                matched = [p for p in self.players if p.hasRank(card.rank)]

                if not matched:
                    print("  Nobody matched!")

                for player in matched:
                    if action == "drink":
                        self._drinkAction(player, drinks)

                    elif action == "give":
                        self._giveAction(player, drinks)

                    elif action == "share":
                        self._shareAction(player, drinks)

    def _drinkAction(self, player: Player, drinks: int) -> None:
        print(f"{player.getName()} matched! Drink {drinks}")
        player.addDrinks(drinks)

    def _giveAction(self, player: Player, drinks: int) -> None:
        print(f"{player.getName()} matched! Give out {drinks} drinks")

        others = self._listPlayers(player)

        print("\nAvailable players:")
        for p in others:
            print(f"- {p.getName()}")

        while True:
            name = _input("Give to (name): ").strip()

            target = next((p for p in others if p.getName().lower() == name.lower()), None)

            if target:
                target.addDrinks(drinks)
                player.addDrinksToGive(drinks)
                print(f"{target.getName()} drinks {drinks}!")
                break

            print("Invalid name, try again")

    def _shareAction(self, player: Player, drinks: int) -> None:
        print(f"{player.getName()} matched! Share {drinks} drinks")

        others = self._listPlayers(player)

        print("\nAvailable players:")
        for p in others:
            print(f"- {p.getName()}")

        while True:
            name = _input("Share with (name): ").strip()

            target = next((p for p in others if p.getName().lower() == name.lower()), None)

            if target:
                player.addDrinks(drinks)
                target.addDrinks(drinks)
                player.addDrinksToGive(drinks)
                print(f"Both {player.getName()} and {target.getName()} drink {drinks}!")
                break

            print("Invalid name, try again")
            
    def _chooseTarget(self, player: Player) -> Player:
        others = self._listPlayers(player)

        print("\nChoose who receives drinks if you are CORRECT:")
        for p in others:
            print(f"- {p.getName()}")

        while True:
            name = _input("Target player (name): ").strip()

            target = next((p for p in others if p.getName().lower() == name.lower()), None)

            if target:
                return target

            print("Invalid name, try again")
                
    def _draw(self, player: Player):
        card = self.deck.drawCard()
        player.addCardToHand(card)
        return card        
    
    def getGameName():
        return "Buja"
    
    def _listPlayers(self, exclude: Player) -> list[Player]:
        return [p for p in self.players if p.getId() != exclude.getId()]