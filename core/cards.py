"""
A standard playing card and its helpers.
"""
from dataclasses import dataclass
from typing import ClassVar, List

SUIT_SYMBOLS = {
    "Hearts": "♥",
    "Diamonds": "♦",
    "Clubs": "♣",
    "Spades": "♠",
}

@dataclass
class Cards:
    """A single playing card with a rank and suit."""
    rank: str
    suit: str
    SUITS: ClassVar[List[str]] = ["Hearts", "Diamonds", "Clubs", "Spades"]
    RANKS: ClassVar[List[str]] = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

    def __str__(self) -> str:
        symbol = SUIT_SYMBOLS.get(self.suit, self.suit)
        return f"{symbol}{self.rank}"

    def isFaceCard(self) -> bool:
        return self.rank in {"J", "Q", "K"}

    def value(self) -> int:
        """Numeric value of the card. Ace is 14, face cards 11–13, numbers as-is."""
        values = {"A": 14, "K": 13, "Q": 12, "J": 11}
        if self.rank in values:
            return values[self.rank]
        return int(self.rank)

    def isRed(self) -> bool:
        return self.suit in {"Hearts", "Diamonds"}

    def isBlack(self) -> bool:
        return self.suit in {"Clubs", "Spades"}