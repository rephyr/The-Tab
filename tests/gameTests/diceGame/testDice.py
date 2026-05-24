import unittest
from games.diceGame.dice import _scoreRoll, _displayScore, _displayClaimScore, _parseClaim, MexicanGame
from core.player import Player
from printing.log import GameLog
from tests.testUtils import SilentTest


class TestScoreRoll(unittest.TestCase):

    def testMexicoBeatsAll(self):
        self.assertEqual(_scoreRoll(2, 1), 1000)
        self.assertEqual(_scoreRoll(1, 2), 1000)
        self.assertGreater(_scoreRoll(2, 1), _scoreRoll(6, 6))

    def testDoublesScoreCorrectly(self):
        self.assertEqual(_scoreRoll(6, 6), 206)
        self.assertEqual(_scoreRoll(1, 1), 201)
        self.assertGreater(_scoreRoll(6, 6), _scoreRoll(5, 5))
        self.assertGreater(_scoreRoll(2, 2), _scoreRoll(1, 1))

    def testDoublesBeatsRegular(self):
        self.assertGreater(_scoreRoll(1, 1), _scoreRoll(6, 5))

    def testRegularScoreUsesHigherDieFirst(self):
        self.assertEqual(_scoreRoll(4, 3), 43)
        self.assertEqual(_scoreRoll(3, 4), 43)

    def testRegularOrdering(self):
        self.assertGreater(_scoreRoll(6, 5), _scoreRoll(6, 4))
        self.assertGreater(_scoreRoll(6, 1), _scoreRoll(5, 4))


class TestDisplayScore(unittest.TestCase):

    def testMexicoLabel(self):
        self.assertIn("Mexico", _displayScore(2, 1))
        self.assertIn("Mexico", _displayScore(1, 2))

    def testDoublesLabel(self):
        result = _displayScore(5, 5)
        self.assertIn("Parit", result)
        self.assertIn("5", result)

    def testRegularShowsScore(self):
        self.assertIn("43", _displayScore(4, 3))
        self.assertIn("43", _displayScore(3, 4))


class TestDisplayClaimScore(unittest.TestCase):

    def testMexico(self):
        self.assertIn("Mexico", _displayClaimScore(1000))

    def testDoubles(self):
        result = _displayClaimScore(206)
        self.assertIn("Parit", result)
        self.assertIn("6", result)

    def testRegular(self):
        result = _displayClaimScore(43)
        self.assertIn("43", result)


class TestParseClaim(unittest.TestCase):

    def testMexicoKeywords(self):
        self.assertEqual(_parseClaim("mexico"), 1000)
        self.assertEqual(_parseClaim("meksiko"), 1000)
        self.assertEqual(_parseClaim("Mexico"), 1000)

    def testRollTwoOneIsMexico(self):
        self.assertEqual(_parseClaim("21"), 1000)
        self.assertEqual(_parseClaim("12"), 1000)

    def testDoubles(self):
        self.assertEqual(_parseClaim("55"), _scoreRoll(5, 5))
        self.assertEqual(_parseClaim("66"), _scoreRoll(6, 6))

    def testRegular(self):
        self.assertEqual(_parseClaim("43"), _scoreRoll(4, 3))
        self.assertEqual(_parseClaim("65"), _scoreRoll(6, 5))

    def testInvalidDiceValues(self):
        self.assertIsNone(_parseClaim("77"))
        self.assertIsNone(_parseClaim("70"))
        self.assertIsNone(_parseClaim("07"))

    def testInvalidFormats(self):
        self.assertIsNone(_parseClaim("abc"))
        self.assertIsNone(_parseClaim("4"))
        self.assertIsNone(_parseClaim(""))
        self.assertIsNone(_parseClaim("123"))


class TestChallengeResolution(SilentTest):
    """Tests for who drinks and how much on a challenge."""

    def _makeGame(self):
        players = [Player(1, "Alice"), Player(2, "Bob")]
        log = GameLog()
        return MexicanGame(players=players, log=log), players, log

    def _collectEvents(self, log, eventType):
        return [e for e in log.events if isinstance(e, eventType)]

    def testClaimerDrinksWhenLying(self):
        game, players, log = self._makeGame()
        alice, bob = players
        actual = _scoreRoll(4, 3)   # 43
        claimed = _scoreRoll(6, 5)  # 65 — a lie
        self.assertLess(actual, claimed)
        wasMexico = claimed == 1000 or actual == 1000
        drinks = game._drinkAmount(wasMexico)
        loser = alice if actual < claimed else bob
        loser.addDrinks(drinks)
        self.assertEqual(alice.getDrinksTaken(), 1)
        self.assertEqual(bob.getDrinksTaken(), 0)

    def testChallengerDrinksWhenTruth(self):
        game, players, log = self._makeGame()
        alice, bob = players
        actual = _scoreRoll(6, 5)   # 65
        claimed = _scoreRoll(4, 3)  # 43 — an understatement (still truth, actual >= claimed)
        wasMexico = claimed == 1000 or actual == 1000
        drinks = game._drinkAmount(wasMexico)
        loser = alice if actual < claimed else bob
        loser.addDrinks(drinks)
        self.assertEqual(bob.getDrinksTaken(), 1)
        self.assertEqual(alice.getDrinksTaken(), 0)

    def testMexicoDoublesTheDrinks(self):
        game, players, _ = self._makeGame()
        self.assertEqual(game._drinkAmount(wasMexico=True), 2)
        self.assertEqual(game._drinkAmount(wasMexico=False), 1)

    def testMexicoFlagSetWhenClaimedIsMexico(self):
        claimed = 1000
        actual = _scoreRoll(4, 3)
        wasMexico = claimed == 1000 or actual == 1000
        self.assertTrue(wasMexico)

    def testMexicoFlagSetWhenActualIsMexico(self):
        claimed = _scoreRoll(4, 3)
        actual = 1000
        wasMexico = claimed == 1000 or actual == 1000
        self.assertTrue(wasMexico)

    def testNoMexicoFlagOnNormalRound(self):
        claimed = _scoreRoll(6, 5)
        actual = _scoreRoll(4, 3)
        wasMexico = claimed == 1000 or actual == 1000
        self.assertFalse(wasMexico)


if __name__ == "__main__":
    unittest.main()
