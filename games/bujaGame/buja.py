from core.game import Game
from core.deck import Deck
from core.player import Player
from dataclasses import dataclass, field
from core.cards import Cards
DRINKAMOUNT = 2

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
        print("\nphase 1")
        
        print("Red or Black?")
        
        for player in self.players: 
            print(f"\n{player.getName()} turn")
            self._redOrBlack(player)
            
        print("\nphase2")
        
        print("Higher or Lower")
        
        for player in self.players: 
            print(f"\n{player.getName()} turn")
            self._higherOrLower(player)
        
        print("\nphase3")
        for player in self.players: 
            print(f"\n{player.getName()} turn")
            self._insideOrOutside(player)
        
        print("\nphase4")
        for player in self.players: 
            print(f"\n{player.getName()} turn")
            self._suit(player)
            
        print(f"\nHands for each player:\n")
        for player in self.players:
            hand_str = ", ".join(str(c) for c in player.getHand())
            print(f"{player.getName()}: {hand_str}")
            
        print(f"\nDrink tally:\n")
        for player in self.players:
            print(f"{player.getName()}: drank {player.getDrinksTaken()} | gave out {player.drinksToGive}")

                   
    def _redOrBlack(self, player: Player) -> None:
        guess = ""
        
        while guess not in ("r","b"):
            guess = _input("Red or Black? (r/b)").strip().lower()
            
        card = self._draw(player)
        print(f"Card: {card}")
        
        if (guess == "r" and card.isRed()) or (guess == "b" and card.isBlack()):
            print(f"Correct give out {DRINKAMOUNT}")
            player.addDrinksToGive(DRINKAMOUNT)
        else:
            print(f"Wrong, drink {DRINKAMOUNT}")
            player.addDrinks(DRINKAMOUNT)

    def _higherOrLower(self, player: Player) -> None:
        last = player.getHand()[-1]
        print(f"Your last card: {last}")
        guess = ""
        while guess not in ("h", "l"):
            guess = _input("Higher or Lower? (h/l)").strip().lower()
            
        card = self._draw(player)
        
        print(f"Drawn card: {card}")

        if card.value() == last.value():
            toDrink = DRINKAMOUNT * 2
            print(f"Same drink {toDrink}")
            player.addDrinks(toDrink)
            
        elif (guess == "h" and card.value() > last.value()) or (guess == "l" and card.value() < last.value()):
            print(f"Correct give out {DRINKAMOUNT}")
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
        
        if v == low.value() or v == high.value():
            toDrink = DRINKAMOUNT * 2
            print(f"On the line drink {toDrink}")
            player.addDrinks(toDrink)
        elif (guess == "i" and low.value() < v < high.value()) or (guess == "o" and (v < low.value() or v > high.value())):
            print(f"Correct: give out {DRINKAMOUNT}")
            player.addDrinksToGive(DRINKAMOUNT)
        else: 
            print(f"Wrong: drink {DRINKAMOUNT}")
            player.addDrinks(DRINKAMOUNT)
    
    def _suit(self, player: Player):
        suits = [s.lower() for s in Cards.SUITS]
        print("Suits: Hearts, Diamonds, Clubs, Spades")
        guess = ""
        
        while guess not in suits:
            guess = _input("Guess suit: ").strip().lower()
        
        card = self._draw(player)
        print(f"Card: {card}")
        
        if guess == card.suit.lower():
            print(f"Correct: Give out {DRINKAMOUNT} drink")
            player.addDrinksToGive(DRINKAMOUNT)
        else:
            print(f"Wrong: drink {DRINKAMOUNT}")
            player.addDrinks(DRINKAMOUNT)
            
    def _draw(self, player: Player):
        card = self.deck.drawCard()
        player.addCardToHand(card)
        return card        
    
    def getGameName():
        return "Buja"