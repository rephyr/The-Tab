import unittest
from tests.testUtils import SilentTest
from unittest.mock import patch
from core.player import Player
from core.events import GameStartEvent, GameEndEvent, RaceStartEvent, HorseEventFiredEvent, RaceFinishedEvent
from games.ravitGame.ravit import RavitGame
from printing.log import GameLog


def makeRavitWithLog():
    players = [Player(1, "Testi"), Player(2, "Matti")]
    log = GameLog()
    game = RavitGame(players=players, config={"horseCount": 2, "trackLength": 5, "maxBet": 3, "eventChance": 0.0}, log=log)
    return game, log


def _runWithInputs(game, inputs):
    with patch("builtins.input", side_effect=inputs), \
         patch("builtins.print"):
        game.playRound()


class TestRavitLogIntegration(SilentTest):

    def testFirstEventIsGameStart(self):
        game, log = makeRavitWithLog()
        _runWithInputs(game, ["1", "1", "2", "1", ""] * 20)
        self.assertIsInstance(log.events[0], GameStartEvent)

    def testGameStartHasPlayerNames(self):
        game, log = makeRavitWithLog()
        _runWithInputs(game, ["1", "1", "2", "1", ""] * 20)
        self.assertIn("Testi", log.events[0].players)
        self.assertIn("Matti", log.events[0].players)

    def testLastEventIsGameEnd(self):
        game, log = makeRavitWithLog()
        _runWithInputs(game, ["1", "1", "2", "1", ""] * 20)
        self.assertIsInstance(log.events[-1], GameEndEvent)

    def testRaceStartEventPresent(self):
        game, log = makeRavitWithLog()
        _runWithInputs(game, ["1", "1", "2", "1", ""] * 20)
        raceStarts = [e for e in log.events if isinstance(e, RaceStartEvent)]
        self.assertEqual(len(raceStarts), 1)

    def testRaceStartCarriesHorsesAndBets(self):
        game, log = makeRavitWithLog()
        _runWithInputs(game, ["1", "1", "2", "1", ""] * 20)
        rs = next(e for e in log.events if isinstance(e, RaceStartEvent))
        self.assertEqual(len(rs.horses), 2)
        self.assertEqual(len(rs.bets), 2)

    def testRaceFinishedEventPresent(self):
        game, log = makeRavitWithLog()
        _runWithInputs(game, ["1", "1", "2", "1", ""] * 20)
        finished = [e for e in log.events if isinstance(e, RaceFinishedEvent)]
        self.assertEqual(len(finished), 1)

    def testRaceFinishedHasFinalPositions(self):
        game, log = makeRavitWithLog()
        _runWithInputs(game, ["1", "1", "2", "1", ""] * 20)
        rf = next(e for e in log.events if isinstance(e, RaceFinishedEvent))
        self.assertEqual(len(rf.finalPositions), 2)

    def testGameEndScoresHaveBothPlayers(self):
        game, log = makeRavitWithLog()
        _runWithInputs(game, ["1", "1", "2", "1", ""] * 20)
        ge = log.events[-1]
        names = [s["name"] for s in ge.scores]
        self.assertIn("Testi", names)
        self.assertIn("Matti", names)

    def testHorseEventFiredWhenForced(self):
        game, log = makeRavitWithLog()
        game.config["eventChance"] = 1.0
        with patch("random.choices", return_value=["boost"]):
            _runWithInputs(game, ["1", "1", "2", "1", ""] * 20)
        events = [e for e in log.events if isinstance(e, HorseEventFiredEvent)]
        self.assertGreater(len(events), 0)

    def testNoLogDoesNotCrash(self):
        players = [Player(1, "Testi"), Player(2, "Matti")]
        game = RavitGame(
            players=players,
            config={"horseCount": 2, "trackLength": 5, "maxBet": 3, "eventChance": 0.0},
        )
        _runWithInputs(game, ["1", "1", "2", "1", ""] * 20)


class TestRavitFullPipeline(SilentTest):

    def testGameRunsEndToEnd(self):
        game, log = makeRavitWithLog()
        _runWithInputs(game, ["1", "1", "2", "1", ""] * 20)

        data = log.toDict()
        self.assertIsNotNone(data["timestamp"])
        self.assertIn("Testi", data["players"])
        self.assertEqual(len(data["scores"]), 2)

    def testToDictScoresPopulated(self):
        game, log = makeRavitWithLog()
        _runWithInputs(game, ["1", "1", "2", "1", ""] * 20)

        data = log.toDict()
        for score in data["scores"]:
            self.assertIn("name", score)
            self.assertIn("drank", score)
            self.assertIn("gave", score)


if __name__ == "__main__":
    unittest.main()
