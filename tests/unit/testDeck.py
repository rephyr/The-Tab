import unittest
from core.deck import Deck
from core.cards import Cards
from tests.testUtils import SilentTest

class TestDeck(SilentTest):

    def setUp(self):
        super().setUp()
        self.deck = Deck()
        self.deck.buildDeck()
 
    def testBuildDeckHas52Cards(self):
        self.assertEqual(self.deck.cardsRemaining(), 52)
 
    def testBuildDeckHasAllSuitsAndRanks(self):
        suits = {c.suit for c in self.deck.seeDeck()}
        ranks = {c.rank for c in self.deck.seeDeck()}
        self.assertEqual(suits, set(Cards.SUITS))
        self.assertEqual(ranks, set(Cards.RANKS))
 
    def testDrawCardReducesCount(self):
        self.deck.drawCard()
        self.assertEqual(self.deck.cardsRemaining(), 51)
 
    def testDrawCardReturnsCard(self):
        card = self.deck.drawCard()
        self.assertIsInstance(card, Cards)
 
    def testSeeTopCardDoesNotRemove(self):
        top = self.deck.seeTopCard()
        self.assertEqual(self.deck.cardsRemaining(), 52)
        self.assertIsInstance(top, Cards)
 
    def testResetDeckRestores52Cards(self):
        self.deck.drawCard()
        self.deck.drawCard()
        self.deck.resetDeck()
        self.assertEqual(self.deck.cardsRemaining(), 52)
 
    def testShuffleDeckChangesOrder(self):
        original = list(self.deck.seeDeck())
        self.deck.shuffleDeck()
        shuffled = self.deck.seeDeck()
        self.assertNotEqual(original, shuffled)
        
class TestMultiDeck(SilentTest):
    def testTwoDecksBuild104Cards(self):
        deck = Deck(deckCount=2)
        deck.buildDeck()
        self.assertEqual(deck.cardsRemaining(), 104)

    def testThreeDecksBuild156Cards(self):
        deck = Deck(deckCount=3)
        deck.buildDeck()
        self.assertEqual(deck.cardsRemaining(), 156)

    def testTwoDecksHasDuplicates(self):
        deck = Deck(deckCount=2)
        deck.buildDeck()
        ranks = [c.rank for c in deck.seeDeck()]
        self.assertEqual(ranks.count("A"), 8)

    def testResetDeckRespectsMultipleDeckCount(self):
        deck = Deck(deckCount=2)
        deck.buildDeck()
        deck.drawCard()
        deck.resetDeck()
        self.assertEqual(deck.cardsRemaining(), 104)


if __name__ == "__main__":
    unittest.main()