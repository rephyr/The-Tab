import unittest
from unittest.mock import patch
from core.cards import Cards
from core.deck import Deck
from core.player import Player
from games.bujaGame.buja import Buja

def makePlayer(id=1, name="Testi Timo"):
    return Player(id=id, name=name)

def makeCard(rank, suit="Hearts"):
    return Cards(rank, suit)

def makeBuja(players=None):
    deck = Deck()
    deck.resetDeck()
    if players is None:
        players = [makePlayer(1, "Alice"), makePlayer(2, "Bob")]
    return Buja(name="Buja", players=players, deck=deck)
 
 
class TestBujaRedOrBlack(unittest.TestCase):
 
    def test_correct_red_gives_drink(self):
        game = makeBuja()
        player = game.players[0]
        red_card = makeCard("A", "Hearts")
        with patch("games.bujaGame.buja._input", return_value="r"), \
             patch.object(game, "_draw", return_value=red_card):
            game._redOrBlack(player)
        self.assertEqual(player.drinksToGive, 1)
        self.assertEqual(player.getDrinksTaken(), 0)
 
    def test_wrong_red_drinks(self):
        game = makeBuja()
        player = game.players[0]
        black_card = makeCard("A", "Spades")
        with patch("games.bujaGame.buja._input", return_value="r"), \
             patch.object(game, "_draw", return_value=black_card):
            game._redOrBlack(player)
        self.assertEqual(player.getDrinksTaken(), 1)
        self.assertEqual(player.drinksToGive, 0)
 
    def test_correct_black_gives_drink(self):
        game = makeBuja()
        player = game.players[0]
        black_card = makeCard("A", "Spades")
        with patch("games.bujaGame.buja._input", return_value="b"), \
             patch.object(game, "_draw", return_value=black_card):
            game._redOrBlack(player)
        self.assertEqual(player.drinksToGive, 1)
 
 
class TestBujaHigherOrLower(unittest.TestCase):
 
    def setUp(self):
        self.game = makeBuja()
        self.player = self.game.players[0]
        self.player.addCardToHand(makeCard("7"))
 
    def test_correct_higher(self):
        with patch("games.bujaGame.buja._input", return_value="h"), \
             patch.object(self.game, "_draw", return_value=makeCard("9")):
            self.game._higherOrLower(self.player)
        self.assertEqual(self.player.drinksToGive, 1)
 
    def test_correct_lower(self):
        with patch("games.bujaGame.buja._input", return_value="l"), \
             patch.object(self.game, "_draw", return_value=makeCard("5")):
            self.game._higherOrLower(self.player)
        self.assertEqual(self.player.drinksToGive, 1)
 
    def test_wrong_higher(self):
        with patch("games.bujaGame.buja._input", return_value="h"), \
             patch.object(self.game, "_draw", return_value=makeCard("5")):
            self.game._higherOrLower(self.player)
        self.assertEqual(self.player.getDrinksTaken(), 1)
 
    def test_same_value_drinks_double(self):
        with patch("games.bujaGame.buja._input", return_value="h"), \
             patch.object(self.game, "_draw", return_value=makeCard("7")):
            self.game._higherOrLower(self.player)
        self.assertEqual(self.player.getDrinksTaken(), 2)
 
 
class TestBujaInsideOrOutside(unittest.TestCase):
 
    def setUp(self):
        self.game = makeBuja()
        self.player = self.game.players[0]
        self.player.addCardToHand(makeCard("3"))
        self.player.addCardToHand(makeCard("9"))
 
    def test_correct_inside(self):
        with patch("games.bujaGame.buja._input", return_value="i"), \
             patch.object(self.game, "_draw", return_value=makeCard("6")):
            self.game._insideOrOutside(self.player)
        self.assertEqual(self.player.drinksToGive, 1)
 
    def test_correct_outside(self):
        with patch("games.bujaGame.buja._input", return_value="o"), \
             patch.object(self.game, "_draw", return_value=makeCard("2")):
            self.game._insideOrOutside(self.player)
        self.assertEqual(self.player.drinksToGive, 1)
 
    def test_wrong_inside(self):
        with patch("games.bujaGame.buja._input", return_value="i"), \
             patch.object(self.game, "_draw", return_value=makeCard("2")):
            self.game._insideOrOutside(self.player)
        self.assertEqual(self.player.getDrinksTaken(), 1)
 
    def test_on_the_line_drinks_double(self):
        with patch("games.bujaGame.buja._input", return_value="i"), \
             patch.object(self.game, "_draw", return_value=makeCard("3")):
            self.game._insideOrOutside(self.player)
        self.assertEqual(self.player.getDrinksTaken(), 2)
 
 
class TestBujaSuit(unittest.TestCase):
 
    def test_correct_suit_gives_drink(self):
        game = makeBuja()
        player = game.players[0]
        with patch("games.bujaGame.buja._input", return_value="hearts"), \
             patch.object(game, "_draw", return_value=makeCard("A", "Hearts")):
            game._suit(player)
        self.assertEqual(player.drinksToGive, 1)
 
    def test_wrong_suit_drinks(self):
        game = makeBuja()
        player = game.players[0]
        with patch("games.bujaGame.buja._input", return_value="spades"), \
             patch.object(game, "_draw", return_value=makeCard("A", "Hearts")):
            game._suit(player)
        self.assertEqual(player.getDrinksTaken(), 1)
 
 
class TestBujaBoardActions(unittest.TestCase):
 
    def setUp(self):
        self.game = makeBuja()
        self.alice = self.game.players[0]
        self.bob = self.game.players[1]
 
    def test_drinkAction(self):
        self.game._drinkAction(self.alice, 4)
        self.assertEqual(self.alice.getDrinksTaken(), 4)
 
    def test_giveAction(self):
        with patch("games.bujaGame.buja._input", return_value="1"):
            self.game._giveAction(self.alice, 4)
        self.assertEqual(self.bob.getDrinksTaken(), 4)
        self.assertEqual(self.alice.drinksToGive, 4)
 
    def test_shareAction(self):
        with patch("games.bujaGame.buja._input", return_value="1"):
            self.game._shareAction(self.alice, 4)
        self.assertEqual(self.alice.getDrinksTaken(), 4)
        self.assertEqual(self.bob.getDrinksTaken(), 4)
        self.assertEqual(self.alice.drinksToGive, 4)
 
 
if __name__ == "__main__":
    unittest.main()