import unittest
from core.player import Player
from core.cards import Cards

def makePlayer(id=1, name="Testi Timo"):
    return Player(id=id, name=name)

def makeCard(rank, suit="Hearts"):
    return Cards(rank, suit)

class TestPlayer(unittest.TestCase):
    
    def setUp(self):
        self.player = makePlayer(1, "Testi Timo")
 
    def test_getName(self):
        self.assertEqual(self.player.getName(), "Testi Timo")
 
    def test_getId(self):
        self.assertEqual(self.player.getId(), 1)
 
    def test_addDrinks(self):
        self.player.addDrinks(2)
        self.player.addDrinks(3)
        self.assertEqual(self.player.getDrinksTaken(), 5)
 
    def test_addDrinksToGive(self):
        self.player.addDrinksToGive(2)
        self.assertEqual(self.player.drinksToGive, 2)
 
    def test_addCardToHand(self):
        card = makeCard("A")
        self.player.addCardToHand(card)
        self.assertIn(card, self.player.getHand())
 
    def test_clearHand(self):
        self.player.addCardToHand(makeCard("A"))
        self.player.clearHand()
        self.assertEqual(self.player.getHand(), [])
 
    def test_hasRank_true(self):
        self.player.addCardToHand(makeCard("A"))
        self.assertTrue(self.player.hasRank("A"))
 
    def test_hasRank_false(self):
        self.player.addCardToHand(makeCard("A"))
        self.assertFalse(self.player.hasRank("K"))
 
    def test_setDrinksTaken(self):
        self.player.addDrinks(5)
        self.player.setDrinksTaken(0)
        self.assertEqual(self.player.getDrinksTaken(), 0)

if __name__ == "__main__":
    unittest.main()