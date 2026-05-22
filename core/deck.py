
"""
A standard 52-card deck with optional multi-deck support.
"""
from dataclasses import dataclass, field
from random import shuffle
from typing import List, Optional

from .cards import Card

@dataclass
class Deck:
    """Holds and manages one or more combined decks of cards."""
    cards: List[Card] = field(default_factory=list)
    deckCount: int = 1

    def buildDeck(self) -> None:
        """Fill the deck with deckCount × 52 cards."""
        self.cards.clear()
        for _ in range(self.deckCount):
            for suit in Card.SUITS:
                for rank in Card.RANKS:
                    self.cards.append(Card(rank=rank, suit=suit))

    def shuffleDeck(self) -> None:
        shuffle(self.cards)

    def resetDeck(self) -> None:
        """Rebuild and shuffle the deck (respects deckCount)."""
        self.buildDeck()
        self.shuffleDeck()

    def drawCard(self) -> Optional[Card]:
        """Remove and return the top card, or None if the deck is empty."""
        if not self.cards:
            return None
        return self.cards.pop()

    def seeTopCard(self) -> Optional[Card]:
        if not self.cards:
            return None
        return self.cards[-1]
    
    def seeDeck(self) -> List[Card]:
        return list(self.cards)

    def cardsRemaining(self) -> int:
        return len(self.cards)