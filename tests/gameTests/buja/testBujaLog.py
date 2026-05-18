import unittest
from unittest.mock import patch
from core.cards import Cards
from core.deck import Deck
from core.player import Player
from core.events import GameStartEvent, GameEndEvent, GuessEvent, DrinkEvent, GiveEvent
from games.bujaGame.buja import Buja
from printing.log import GameLog
from printing.printer import _StdoutPrinter
from printing.formatter import formatReceipt


def makePlayer(id=1, name="Test"):
    return Player(id=id, name=name)


def makeCard(rank, suit="Hearts"):
    return Cards(rank, suit)


def makeBujaWithLog():
    deck = Deck()
    deck.resetDeck()
    log = GameLog()
    players = [makePlayer(1, "Alice"), makePlayer(2, "Bob")]
    game = Buja(players=players, deck=deck, config={}, log=log)
    return game, log


class TestBujaUsesLog(unittest.TestCase):

    def test_log_receives_events_after_round(self):
        game, log = makeBujaWithLog()

        with patch.object(game, "_redOrBlack"), \
             patch.object(game, "_higherOrLower"), \
             patch.object(game, "_insideOrOutside"), \
             patch.object(game, "_suit"), \
             patch.object(game, "_board"), \
             patch("builtins.input", return_value=""):

            game.playRound()

        self.assertGreater(len(log.events), 0)

    def test_log_starts_with_game_start_event(self):
        game, log = makeBujaWithLog()

        with patch.object(game, "_redOrBlack"), \
             patch.object(game, "_higherOrLower"), \
             patch.object(game, "_insideOrOutside"), \
             patch.object(game, "_suit"), \
             patch.object(game, "_board"), \
             patch("builtins.input", return_value=""):

            game.playRound()

        self.assertIsInstance(log.events[0], GameStartEvent)

    def test_log_ends_with_game_end_event(self):
        game, log = makeBujaWithLog()

        with patch.object(game, "_redOrBlack"), \
             patch.object(game, "_higherOrLower"), \
             patch.object(game, "_insideOrOutside"), \
             patch.object(game, "_suit"), \
             patch.object(game, "_board"), \
             patch("builtins.input", return_value=""):

            game.playRound()

        self.assertIsInstance(log.events[-1], GameEndEvent)

    def test_game_start_event_has_player_names(self):
        game, log = makeBujaWithLog()

        with patch.object(game, "_redOrBlack"), \
             patch.object(game, "_higherOrLower"), \
             patch.object(game, "_insideOrOutside"), \
             patch.object(game, "_suit"), \
             patch.object(game, "_board"), \
             patch("builtins.input", return_value=""):

            game.playRound()

        start = log.events[0]
        self.assertIn("Alice", start.players)
        self.assertIn("Bob", start.players)

    def test_no_log_does_not_crash(self):
        deck = Deck()
        deck.resetDeck()
        game = Buja(players=[makePlayer(1, "Alice"), makePlayer(2, "Bob")], deck=deck, config={})

        with patch.object(game, "_redOrBlack"), \
             patch.object(game, "_higherOrLower"), \
             patch.object(game, "_insideOrOutside"), \
             patch.object(game, "_suit"), \
             patch.object(game, "_board"), \
             patch("builtins.input", return_value=""):

            game.playRound()

    def test_wrong_guess_emits_drink_event(self):
        game, log = makeBujaWithLog()
        player = game.players[0]

        with patch("builtins.input", return_value="r"), \
             patch("builtins.print"), \
             patch.object(game, "_draw", return_value=makeCard("A", "Spades")), \
             patch.object(game, "_chooseTarget", return_value=game.players[1]):

            game._redOrBlack(player)

        drink_events = [e for e in log.events if isinstance(e, DrinkEvent)]
        self.assertEqual(len(drink_events), 1)
        self.assertEqual(drink_events[0].player, "Alice")

    def test_correct_guess_emits_give_event(self):
        game, log = makeBujaWithLog()
        player = game.players[0]

        with patch("builtins.input", return_value="r"), \
             patch("builtins.print"), \
             patch.object(game, "_draw", return_value=makeCard("A", "Hearts")), \
             patch.object(game, "_chooseTarget", return_value=game.players[1]):

            game._redOrBlack(player)

        give_events = [e for e in log.events if isinstance(e, GiveEvent)]
        self.assertEqual(len(give_events), 1)
        self.assertEqual(give_events[0].giver, "Alice")
        self.assertEqual(give_events[0].receiver, "Bob")


class TestFullPipeline(unittest.TestCase):

    def test_game_plays_itself_and_prints_receipt(self):
        deck = Deck()
        deck.resetDeck()
        log = GameLog()
        players = [makePlayer(1, "Alice"), makePlayer(2, "Bob")]
        game = Buja(players=players, deck=deck, config={}, log=log)

        # 2 players × 4 phases = 8 guesses, then 9 enter presses for the board
        inputs = ["r", "b", "h", "l", "i", "o", "h", "d"] + [""] * 9

        with patch("builtins.input", side_effect=inputs), \
             patch("builtins.print"), \
             patch.object(game, "_chooseTarget", return_value=game.players[1]):
            game.playRound()

        data = log.toDict()
        p = _StdoutPrinter()

        # should not raise
        formatReceipt(data, p)

        self.assertEqual(data["players"], ["Alice", "Bob"])
        self.assertEqual(len(data["board"]), 9)
        self.assertEqual(len(data["scores"]), 2)
        self.assertIsNotNone(data["timestamp"])


if __name__ == "__main__":
    unittest.main()
