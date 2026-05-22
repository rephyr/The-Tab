import unittest
from core.player import Player
from core.cards import Card
from tests.testUtils import SilentTest

def makePlayer(id=1, name="Testi Timo"):
    return Player(id=id, name=name)

def makeCard(rank, suit="Hearts"):
    return Card(rank, suit)

class TestPlayer(SilentTest):

    def setUp(self):
        super().setUp()
        self.player = makePlayer(1, "Testi Timo")
 
    def testGetName(self):
        self.assertEqual(self.player.getName(), "Testi Timo")
 
    def testGetId(self):
        self.assertEqual(self.player.getId(), 1)
 
    def testAddDrinks(self):
        self.player.addDrinks(2)
        self.player.addDrinks(3)
        self.assertEqual(self.player.getDrinksTaken(), 5)
 
    def testAddDrinksToGive(self):
        self.player.addDrinksToGive(2)
        self.assertEqual(self.player.drinksToGive, 2)
 
    def testAddCardToHand(self):
        card = makeCard("A")
        self.player.addCardToHand(card)
        self.assertIn(card, self.player.getHand())
 
    def testClearHand(self):
        self.player.addCardToHand(makeCard("A"))
        self.player.clearHand()
        self.assertEqual(self.player.getHand(), [])
 
    def testHasRankTrue(self):
        self.player.addCardToHand(makeCard("A"))
        self.assertTrue(self.player.hasRank("A"))
 
    def testHasRankFalse(self):
        self.player.addCardToHand(makeCard("A"))
        self.assertFalse(self.player.hasRank("K"))
 
    def testSetDrinksTaken(self):
        self.player.addDrinks(5)
        self.player.setDrinksTaken(0)
        self.assertEqual(self.player.getDrinksTaken(), 0)

if __name__ == "__main__":
    unittest.main()