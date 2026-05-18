"""
Represents a player in the game — tracks their hand, drinks taken, and drinks given out.
"""
from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING
 
if TYPE_CHECKING:
    from .cards import Cards
 
@dataclass
class Player:
    id: int
    name: str
    drinksTaken: int = 0
    drinksToGive: int = 0
    hand: List["Cards"] = field(default_factory=list)
 
    def getName(self) -> str:
        return self.name
 
    def getId(self) -> int:
        return self.id
 
    def getDrinksTaken(self) -> int:
        return self.drinksTaken
 
    def setName(self, name: str) -> None:
        self.name = name
 
    def setId(self, id: int) -> None:
        self.id = id
 
    def setDrinksTaken(self, drinksTaken: int) -> None:
        self.drinksTaken = drinksTaken
 
    def addDrinks(self, count: int) -> None:
        self.drinksTaken += count
 
    def addDrinksToGive(self, count: int) -> None:
        self.drinksToGive += count
 
    def addCardToHand(self, card: "Cards") -> None:
        self.hand.append(card)
 
    def clearHand(self) -> None:
        self.hand.clear()
 
    def hasRank(self, rank: str) -> bool:
        """True if the player holds at least one card with this rank."""
        return any(c.rank == rank for c in self.hand)
 
    def getHand(self) -> List["Cards"]:
        return self.hand
 
    def __str__(self) -> str:
        hand_str = ", ".join(str(c) for c in self.hand)
        return f"{self.name} | Drinks taken: {self.drinksTaken} | Hand: [{hand_str}]"
 
