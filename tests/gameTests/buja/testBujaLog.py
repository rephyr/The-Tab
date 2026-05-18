import unittest
from unittest.mock import patch
from core.cards import Cards
from core.deck import Deck
from core.player import Player
from core.events import GameStartEvent, GameEndEvent, GuessEvent, DrinkEvent, GiveEvent
from games.bujaGame.buja import Buja
from printing.log import GameLog
from printing.printer import StdoutPrinter
from printing.formatter import formatReceipt

def makePlayer(id=1, name="Test"):
    return Player(id=id, name=name)

def makeCard(rank, suit="Hearts"):
    return Cards(rank, suit)

def makeBujaWithLog():
    deck = Deck()
    deck.resetDeck()
    log = GameLog()
    players = [makePlayer(1, "Testi Matti"), makePlayer(2, "Testi Timo")]
    game = Buja(players=players, deck=deck, config={}, log=log)
    return game, log

class TestBujaUsesLog(unittest.TestCase):

    def testLogReceivesEventsAfterRound(self):
        game, log = makeBujaWithLog()

        with patch.object(game, "_redOrBlack"), \
             patch.object(game, "_higherOrLower"), \
             patch.object(game, "_insideOrOutside"), \
             patch.object(game, "_suit"), \
             patch.object(game, "_board"), \
             patch("builtins.input", return_value=""):

            game.playRound()

        self.assertGreater(len(log.events), 0)

    def testLogStartsWithGameStartEvent(self):
        game, log = makeBujaWithLog()

        with patch.object(game, "_redOrBlack"), \
             patch.object(game, "_higherOrLower"), \
             patch.object(game, "_insideOrOutside"), \
             patch.object(game, "_suit"), \
             patch.object(game, "_board"), \
             patch("builtins.input", return_value=""):

            game.playRound()

        self.assertIsInstance(log.events[0], GameStartEvent)

    def testLogEndsWithGameEndEvent(self):
        game, log = makeBujaWithLog()

        with patch.object(game, "_redOrBlack"), \
             patch.object(game, "_higherOrLower"), \
             patch.object(game, "_insideOrOutside"), \
             patch.object(game, "_suit"), \
             patch.object(game, "_board"), \
             patch("builtins.input", return_value=""):

            game.playRound()

        self.assertIsInstance(log.events[-1], GameEndEvent)

    def testGameStartEventHasPlayerNames(self):
        game, log = makeBujaWithLog()

        with patch.object(game, "_redOrBlack"), \
             patch.object(game, "_higherOrLower"), \
             patch.object(game, "_insideOrOutside"), \
             patch.object(game, "_suit"), \
             patch.object(game, "_board"), \
             patch("builtins.input", return_value=""):

            game.playRound()

        start = log.events[0]
        self.assertIn("Testi Matti", start.players)
        self.assertIn("Testi Timo", start.players)

    def testNoLogDoesNotCrash(self):
        deck = Deck()
        deck.resetDeck()
        game = Buja(players=[makePlayer(1, "Testi Matti"), makePlayer(2, "Testi Timo")], deck=deck, config={})

        with patch.object(game, "_redOrBlack"), \
             patch.object(game, "_higherOrLower"), \
             patch.object(game, "_insideOrOutside"), \
             patch.object(game, "_suit"), \
             patch.object(game, "_board"), \
             patch("builtins.input", return_value=""):

            game.playRound()

    def testWrongGuessEmitsDrinkEvent(self):
        game, log = makeBujaWithLog()
        player = game.players[0]

        with patch("builtins.input", return_value="r"), \
             patch("builtins.print"), \
             patch.object(game, "_draw", return_value=makeCard("A", "Spades")), \
             patch.object(game, "_chooseTarget", return_value=game.players[1]):

            game._redOrBlack(player)

        drinkEvents = [e for e in log.events if isinstance(e, DrinkEvent)]
        self.assertEqual(len(drinkEvents), 1)
        self.assertEqual(drinkEvents[0].player, "Testi Matti")

    def testCorrectGuessEmitsGiveEvent(self):
        game, log = makeBujaWithLog()
        player = game.players[0]

        with patch("builtins.input", return_value="r"), \
             patch("builtins.print"), \
             patch.object(game, "_draw", return_value=makeCard("A", "Hearts")), \
             patch.object(game, "_chooseTarget", return_value=game.players[1]):

            game._redOrBlack(player)

        giveEvents = [e for e in log.events if isinstance(e, GiveEvent)]
        self.assertEqual(len(giveEvents), 1)
        self.assertEqual(giveEvents[0].giver, "Testi Matti")
        self.assertEqual(giveEvents[0].receiver, "Testi Timo")

class TestFullPipeline(unittest.TestCase):

    def testGamePlaysItselfAndPrintsReceipt(self):
        deck = Deck()
        deck.resetDeck()
        log = GameLog()
        players = [makePlayer(1, "Testi Matti"), makePlayer(2, "Testi Timo")]
        game = Buja(players=players, deck=deck, config={}, log=log)

        # 2 players × 4 phases = 8 guesses, then 10 enter presses for the board (9 cards + 1 final)
        inputs = ["r", "b", "h", "l", "i", "o", "h", "d"] + [""] * 10

        with patch("builtins.input", side_effect=inputs), \
             patch("builtins.print"), \
             patch.object(game, "_chooseTarget", return_value=game.players[1]):
            game.playRound()

        data = log.toDict()
        p = StdoutPrinter()

        # should not raise
        formatReceipt(data, p)

        self.assertEqual(data["players"], ["Testi Matti", "Testi Timo"])
        self.assertEqual(len(data["board"]), 10)
        self.assertEqual(len(data["scores"]), 2)
        self.assertIsNotNone(data["timestamp"])

if __name__ == "__main__":
    unittest.main()
