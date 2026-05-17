"""
player class 
"""
from dataclasses import dataclass

@dataclass
class Player:
    id: int
    name: str
    drinksTaken: int
    
    def getName(self) -> str:
        return self.name

    def getId (self) -> int:
        return self.id
    
    def getDrinksTaken (self) -> int:
        return self.drinksTaken
    
    def setName(self, name: str) -> None:
        self.name = name

    def setId(self, id: int) -> None:
        self.id = id

    def setDrinksTaken(self, drinksTaken: int) -> None:
        self.drinksTaken = drinksTaken