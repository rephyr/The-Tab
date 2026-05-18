
"""
A standard 52-card deck with optional multi-deck support.
"""
from dataclasses import dataclass, field
from random import shuffle
from typing import List, Optional

from .cards import Cards

@dataclass
class Deck:
    """Holds and manages one or more combined decks of cards."""
    cards: List[Cards] = field(default_factory=list)
    deckCount: int = 1

    def buildDeck(self) -> None:
        """Fill the deck with deckCount × 52 cards."""
        self.cards.clear()
        for _ in range(self.deckCount):
            for suit in Cards.SUITS:
                for rank in Cards.RANKS:
                    self.cards.append(Cards(rank=rank, suit=suit))

    def shuffleDeck(self) -> None:
        shuffle(self.cards)

    def resetDeck(self) -> None:
        """Rebuild and shuffle the deck (respects deckCount)."""
        self.buildDeck()
        self.shuffleDeck()

    def drawCard(self) -> Optional[Cards]:
        """Remove and return the top card, or None if the deck is empty."""
        if not self.cards:
            return None
        return self.cards.pop()

    def seeTopCard(self) -> Optional[Cards]:
        if not self.cards:
            return None
        return self.cards[-1]
    
    def seeDeck(self) -> List[Cards]:
        return list(self.cards)

    def printDeck(self) -> None:
        for card in self.cards:
            print(card)
            
    def cardsRemaining(self) -> int:
        return len(self.cards)