
from dataclasses import dataclass, field
from random import shuffle
from typing import List, Optional

from .cards import Cards

@dataclass
class Deck:
    cards: List[Cards] = field(default_factory=list)
    #initialize deck
    def __post_init__(self):
        self.resetDeck()
        
    def buildDeck(self) -> None:
        self.cards.clear()
        for suit in Cards.SUITS:
            for rank in Cards.RANKS:
                self.cards.append(Cards(rank=rank, suit=suit))

    def shuffleDeck(self) -> None:
        shuffle(self.cards)

    def resetDeck(self) -> None:
        self.buildDeck()
        self.shuffleDeck()

    def drawCard(self) -> Cards:
        #never returns none
        if not self.cards:
            self.resetDeck()

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