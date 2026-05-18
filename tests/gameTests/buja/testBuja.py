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
        target = game.players[1]

        with patch("games.bujaGame.buja._input", return_value="r"), \
             patch.object(game, "_draw", return_value=makeCard("A", "Hearts")), \
             patch.object(game, "_chooseTarget", return_value=target):

            game._redOrBlack(player)

        self.assertEqual(target.getDrinksTaken(), 1)

    def test_wrong_red_drinks(self):
        game = makeBuja()
        player = game.players[0]

        with patch("games.bujaGame.buja._input", return_value="r"), \
             patch.object(game, "_draw", return_value=makeCard("A", "Spades")):

            game._redOrBlack(player)

        self.assertEqual(player.getDrinksTaken(), 1)

class TestBujaHigherOrLower(unittest.TestCase):

    def setUp(self):
        self.game = makeBuja()
        self.player = self.game.players[0]
        self.target = self.game.players[1]

        self.player.addCardToHand(makeCard("7"))

    def test_correct_higher(self):
        with patch("games.bujaGame.buja._input", return_value="h"), \
             patch.object(self.game, "_draw", return_value=makeCard("9")), \
             patch.object(self.game, "_chooseTarget", return_value=self.target):

            self.game._higherOrLower(self.player)

        self.assertEqual(self.target.getDrinksTaken(), 1)

    def test_wrong_higher(self):
        with patch("games.bujaGame.buja._input", return_value="h"), \
             patch.object(self.game, "_draw", return_value=makeCard("5")):

            self.game._higherOrLower(self.player)

        self.assertEqual(self.player.getDrinksTaken(), 1)

    def test_same_value(self):
        with patch("games.bujaGame.buja._input", return_value="h"), \
             patch.object(self.game, "_draw", return_value=makeCard("7")):

            self.game._higherOrLower(self.player)

        self.assertEqual(self.player.getDrinksTaken(), 2)

class TestBujaInsideOrOutside(unittest.TestCase):

    def setUp(self):
        self.game = makeBuja()
        self.player = self.game.players[0]
        self.target = self.game.players[1]

        self.player.addCardToHand(makeCard("3"))
        self.player.addCardToHand(makeCard("9"))

    def test_correct_inside(self):
        with patch("games.bujaGame.buja._input", return_value="i"), \
             patch.object(self.game, "_draw", return_value=makeCard("6")), \
             patch.object(self.game, "_chooseTarget", return_value=self.target):

            self.game._insideOrOutside(self.player)

        self.assertEqual(self.target.getDrinksTaken(), 1)

    def test_wrong_inside(self):
        with patch("games.bujaGame.buja._input", return_value="i"), \
             patch.object(self.game, "_draw", return_value=makeCard("2")):

            self.game._insideOrOutside(self.player)

        self.assertEqual(self.player.getDrinksTaken(), 1)

    def test_on_the_line(self):
        with patch("games.bujaGame.buja._input", return_value="i"), \
             patch.object(self.game, "_draw", return_value=makeCard("3")):

            self.game._insideOrOutside(self.player)

        self.assertEqual(self.player.getDrinksTaken(), 2)

class TestBujaSuit(unittest.TestCase):

    def test_correct_suit(self):
        game = makeBuja()
        player = game.players[0]
        target = game.players[1]

        with patch("games.bujaGame.buja._input", return_value="h"), \
             patch.object(game, "_draw", return_value=makeCard("A", "Hearts")), \
             patch.object(game, "_chooseTarget", return_value=target):

            game._suit(player)

        self.assertEqual(target.getDrinksTaken(), 1)

    def test_wrong_suit(self):
        game = makeBuja()
        player = game.players[0]

        with patch("games.bujaGame.buja._input", return_value="s"), \
             patch.object(game, "_draw", return_value=makeCard("A", "Hearts")):

            game._suit(player)

        self.assertEqual(player.getDrinksTaken(), 1)