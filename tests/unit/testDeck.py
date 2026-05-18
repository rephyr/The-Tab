import unittest
from core.deck import Deck
from core.cards import Cards

class TestDeck(unittest.TestCase):
 
    def setUp(self):
        self.deck = Deck()
        self.deck.buildDeck()
 
    def test_buildDeck_has_52_cards(self):
        self.assertEqual(self.deck.cardsRemaining(), 52)
 
    def test_buildDeck_has_all_suits_and_ranks(self):
        suits = {c.suit for c in self.deck.seeDeck()}
        ranks = {c.rank for c in self.deck.seeDeck()}
        self.assertEqual(suits, set(Cards.SUITS))
        self.assertEqual(ranks, set(Cards.RANKS))
 
    def test_drawCard_reduces_count(self):
        self.deck.drawCard()
        self.assertEqual(self.deck.cardsRemaining(), 51)
 
    def test_drawCard_returns_card(self):
        card = self.deck.drawCard()
        self.assertIsInstance(card, Cards)
 
    def test_seeTopCard_does_not_remove(self):
        top = self.deck.seeTopCard()
        self.assertEqual(self.deck.cardsRemaining(), 52)
        self.assertIsInstance(top, Cards)
 
    def test_resetDeck_restores_52_cards(self):
        self.deck.drawCard()
        self.deck.drawCard()
        self.deck.resetDeck()
        self.assertEqual(self.deck.cardsRemaining(), 52)
 
    def test_shuffleDeck_changes_order(self):
        original = list(self.deck.seeDeck())
        self.deck.shuffleDeck()
        shuffled = self.deck.seeDeck()
        self.assertNotEqual(original, shuffled)
        
if __name__ == "__main__":
    unittest.main()