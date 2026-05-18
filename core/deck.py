
"""
A standard 52-card deck.
"""
from dataclasses import dataclass, field
from random import shuffle
from typing import List, Optional

from .cards import Cards

@dataclass
class Deck:
    """Holds and manages a deck of cards. Call resetDeck() before starting a game."""
    cards: List[Cards] = field(default_factory=list)

    def buildDeck(self) -> None:
        self.cards.clear()
        for suit in Cards.SUITS:
            for rank in Cards.RANKS:
                self.cards.append(Cards(rank=rank, suit=suit))

    def shuffleDeck(self) -> None:
        shuffle(self.cards)

    def resetDeck(self) -> None:
        """Rebuild and shuffle the deck back to 52 cards."""
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