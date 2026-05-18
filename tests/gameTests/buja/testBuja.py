import unittest
from unittest.mock import patch
from core.cards import Cards
from core.deck import Deck
from core.player import Player
from games.bujaGame.buja import Buja

def makePlayer(id=1, name="Test"):
    return Player(id=id, name=name)

def makeCard(rank, suit="Hearts"):
    return Cards(rank, suit)

def makeBuja():
    deck = Deck()
    deck.resetDeck()
    players = [makePlayer(1, "Testi Matti"), makePlayer(2, "Testi Timo")]
    return Buja(players=players, deck=deck, config={})


class TestBujaRedOrBlack(unittest.TestCase):

    def testCorrectRed(self):
        game = makeBuja()
        player = game.players[0]

        with patch("builtins.input", return_value="r"), \
             patch("builtins.print"), \
             patch.object(game, "_draw", return_value=makeCard("A", "Hearts")), \
             patch.object(game, "_chooseTarget", return_value=game.players[1]):

            game._redOrBlack(player)

        self.assertEqual(game.players[1].getDrinksTaken(), 1)
        self.assertEqual(player.drinksToGive, 1)

    def testWrongRed(self):
        game = makeBuja()
        player = game.players[0]

        with patch("builtins.input", return_value="r"), \
             patch("builtins.print"), \
             patch.object(game, "_draw", return_value=makeCard("A", "Spades")):

            game._redOrBlack(player)

        self.assertEqual(player.getDrinksTaken(), 1)


class TestBujaHigherOrLower(unittest.TestCase):

    def setUp(self):
        self.game = makeBuja()
        self.player = self.game.players[0]
        self.player.addCardToHand(makeCard("7"))

    def testCorrect(self):
        with patch("builtins.input", return_value="h"), \
             patch("builtins.print"), \
             patch.object(self.game, "_draw", return_value=makeCard("9")), \
             patch.object(self.game, "_chooseTarget", return_value=self.game.players[1]):

            self.game._higherOrLower(self.player)

        self.assertEqual(self.game.players[1].getDrinksTaken(), 1)

    def testWrong(self):
        with patch("builtins.input", return_value="h"), \
             patch("builtins.print"), \
             patch.object(self.game, "_draw", return_value=makeCard("5")):

            self.game._higherOrLower(self.player)

        self.assertEqual(self.player.getDrinksTaken(), 1)

    def testSameValue(self):
        with patch("builtins.input", return_value="h"), \
             patch("builtins.print"), \
             patch.object(self.game, "_draw", return_value=makeCard("7")):

            self.game._higherOrLower(self.player)

        self.assertEqual(self.player.getDrinksTaken(), 2)


class TestBujaInsideOrOutside(unittest.TestCase):

    def setUp(self):
        self.game = makeBuja()
        self.player = self.game.players[0]
        self.player.addCardToHand(makeCard("3"))
        self.player.addCardToHand(makeCard("9"))

    def testCorrect(self):
        with patch("builtins.input", return_value="i"), \
             patch("builtins.print"), \
             patch.object(self.game, "_draw", return_value=makeCard("6")), \
             patch.object(self.game, "_chooseTarget", return_value=self.game.players[1]):

            self.game._insideOrOutside(self.player)

        self.assertEqual(self.game.players[1].getDrinksTaken(), 1)

    def testWrong(self):
        with patch("builtins.input", return_value="i"), \
             patch("builtins.print"), \
             patch.object(self.game, "_draw", return_value=makeCard("2")):

            self.game._insideOrOutside(self.player)

        self.assertEqual(self.player.getDrinksTaken(), 1)

    def testOnTheLine(self):
        with patch("builtins.input", return_value="i"), \
             patch("builtins.print"), \
             patch.object(self.game, "_draw", return_value=makeCard("3")):

            self.game._insideOrOutside(self.player)

        self.assertEqual(self.player.getDrinksTaken(), 2)


class TestBujaSuit(unittest.TestCase):

    def testCorrect(self):
        game = makeBuja()
        player = game.players[0]

        with patch("builtins.input", return_value="h"), \
             patch("builtins.print"), \
             patch.object(game, "_draw", return_value=makeCard("A", "Hearts")), \
             patch.object(game, "_chooseTarget", return_value=game.players[1]):

            game._suit(player)

        self.assertEqual(game.players[1].getDrinksTaken(), 1)

    def testWrong(self):
        game = makeBuja()
        player = game.players[0]

        with patch("builtins.input", return_value="s"), \
             patch("builtins.print"), \
             patch.object(game, "_draw", return_value=makeCard("A", "Hearts")):

            game._suit(player)

        self.assertEqual(player.getDrinksTaken(), 1)


class TestBujaBoard(unittest.TestCase):

    def setUp(self):
        self.game = makeBuja()
        self.testiMatti = self.game.players[0]
        self.testiTimo = self.game.players[1]

    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    def testBoardRuns(self, mockPrint, mockInput):
        with patch.object(self.game.deck, "drawCard", side_effect=[
            makeCard("A"), makeCard("K"), makeCard("Q"),
            makeCard("J"), makeCard("10"), makeCard("9"),
            makeCard("8"), makeCard("7"), makeCard("6")
        ]):
            self.game._board()

        self.assertTrue(self.testiMatti.getDrinksTaken() >= 0)
        self.assertTrue(self.testiTimo.getDrinksTaken() >= 0)


if __name__ == "__main__":
    unittest.main()
