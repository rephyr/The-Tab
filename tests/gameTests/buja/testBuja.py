import unittest
from unittest.mock import patch
from core.cards import Card
from core.deck import Deck
from core.player import Player
from games.bujaGame.buja import Buja
from tests.testUtils import SilentTest

def makePlayer(id=1, name="Test"):
    return Player(id=id, name=name)

def makeCard(rank, suit="Hearts"):
    return Card(rank, suit)

def makeBuja():
    deck = Deck()
    deck.resetDeck()
    players = [makePlayer(1, "Testi Matti"), makePlayer(2, "Testi Timo")]
    return Buja(players=players, deck=deck, config={})

class TestBujaRedOrBlack(SilentTest):

    def testCorrectRed(self):
        game = makeBuja()
        player = game.players[0]

        with patch("builtins.input", side_effect=["r", "1"]), \
             patch("builtins.print"), \
             patch.object(game, "_draw", return_value=makeCard("A", "Hearts")):

            game._redOrBlack(player)
            game._interactiveGivePhase()

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

class TestBujaHigherOrLower(SilentTest):

    def setUp(self):
        super().setUp()
        self.game = makeBuja()
        self.player = self.game.players[0]
        self.player.addCardToHand(makeCard("7"))

    def testCorrect(self):
        with patch("builtins.input", side_effect=["h", "1"]), \
             patch("builtins.print"), \
             patch.object(self.game, "_draw", return_value=makeCard("9")):

            self.game._higherOrLower(self.player)
            self.game._interactiveGivePhase()

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

class TestBujaInsideOrOutside(SilentTest):

    def setUp(self):
        super().setUp()
        self.game = makeBuja()
        self.player = self.game.players[0]
        self.player.addCardToHand(makeCard("3"))
        self.player.addCardToHand(makeCard("9"))

    def testCorrect(self):
        with patch("builtins.input", side_effect=["i", "1"]), \
             patch("builtins.print"), \
             patch.object(self.game, "_draw", return_value=makeCard("6")):

            self.game._insideOrOutside(self.player)
            self.game._interactiveGivePhase()

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

class TestBujaSuit(SilentTest):

    def testCorrect(self):
        game = makeBuja()
        player = game.players[0]

        with patch("builtins.input", side_effect=["h", "1"]), \
             patch("builtins.print"), \
             patch.object(game, "_draw", return_value=makeCard("A", "Hearts")):

            game._suit(player)
            game._interactiveGivePhase()

        self.assertEqual(game.players[1].getDrinksTaken(), 1)

    def testWrong(self):
        game = makeBuja()
        player = game.players[0]

        with patch("builtins.input", return_value="s"), \
             patch("builtins.print"), \
             patch.object(game, "_draw", return_value=makeCard("A", "Hearts")):

            game._suit(player)

        self.assertEqual(player.getDrinksTaken(), 1)

class TestBujaBoard(SilentTest):

    def setUp(self):
        super().setUp()
        self.game = makeBuja()
        self.testiMatti = self.game.players[0]
        self.testiTimo = self.game.players[1]

    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    def testBoardRuns(self, _mockPrint, _mockInput):
        with patch.object(self.game.deck, "drawCard", side_effect=[
            makeCard("A"), makeCard("K"), makeCard("Q"),
            makeCard("J"), makeCard("10"), makeCard("9"),
            makeCard("8"), makeCard("7"), makeCard("6"),
            makeCard("5"),
        ]):
            self.game._board()

        self.assertTrue(self.testiMatti.getDrinksTaken() >= 0)
        self.assertTrue(self.testiTimo.getDrinksTaken() >= 0)

class TestBujaGivePhaseTiming(SilentTest):
    def testGivePhaseCalledAfterEachOfFourGuessPhases(self):
        game = makeBuja()
        call_count = [0]
        game._interactiveGivePhase = lambda: call_count.__setitem__(0, call_count[0] + 1)
        game._board = lambda: None

        # 2 players × 4 phases = 8 per-player calls, no post-board call
        # each turn ends with a "press Enter" pause → interleave with ""
        inputs = ["r", "", "b", "", "h", "", "l", "", "i", "", "o", "", "h", "", "s", ""]
        with patch.object(game.deck, "drawCard", return_value=makeCard("A", "Hearts")), \
             patch("builtins.input", side_effect=inputs):
            game.playRound()

        self.assertEqual(call_count[0], 8)

    def testBoardJaaGivesImmediately(self):
        """Board 'jaa' card asks for a target immediately; pendingGive stays 0."""
        game = makeBuja()
        testiMatti = game.players[0]
        testiTimo = game.players[1]

        # All phase draws are "A Hearts" so both players hold rank "A".
        # Board jaa card is also "A" → both players match and both choose targets.
        board_cards = [makeCard("2"), makeCard("A"), makeCard("3"),
                       makeCard("4"), makeCard("5"), makeCard("6"),
                       makeCard("7"), makeCard("8"), makeCard("9"),
                       makeCard("10")]

        # Full input sequence:
        # ph1: Matti "r" (correct→give→"1"→enter), Timo "b" (wrong→enter)
        # ph2: Matti "h" (same value→enter), Timo "l" (same value→enter)
        # ph3: Matti "i" (boundary→enter), Timo "o" (boundary→enter)
        # ph4: Matti "h" (correct→give→"1"→enter), Timo "s" (wrong→enter)
        # board: Enter×2 then "1"+"1" for both jaa targets, then Enter×8
        all_inputs = [
            "r", "1", "", "b", "",    # phase 1
            "h", "", "l", "",         # phase 2
            "i", "", "o", "",         # phase 3
            "h", "1", "", "s", "",   # phase 4
            "", "",                   # reveal juo card, reveal jaa card
            "1", "1",                 # Matti→Timo, Timo→Matti (jaa immediate)
            "", "", "", "", "", "", "", "",  # remaining board reveals
        ]

        with patch.object(game.deck, "drawCard", side_effect=(
            [makeCard("A", "Hearts")] * 8 + board_cards
        )), patch("builtins.input", side_effect=all_inputs), \
             patch("builtins.print"):
            game.playRound()

        self.assertEqual(testiMatti.pendingGive, 0)
        self.assertEqual(testiTimo.pendingGive, 0)
        self.assertGreater(testiMatti.drinksToGive, 0)


if __name__ == "__main__":
    unittest.main()
