import unittest
from unittest.mock import patch
from core.player import Player
from core.events import GameEndEvent
from games.taskGame.taskGame import TaskGame

DUMMY_TASKS = [
    {"title": "Test Task", "description": "Do something.", "players": 1},
    {"title": "Pair Task", "description": "Do something together.", "players": 2},
    {"title": "All Task", "description": "Everyone does something.", "players": "all"},
]


def makePlayers(*names):
    return [Player(i + 1, name) for i, name in enumerate(names)]


class TestTaskGameRuns(unittest.TestCase):
    def testGameCompletes(self):
        """Game runs to completion without errors."""
        game = TaskGame(players=makePlayers("Testi Timo", "Testi Teppo"))
        with patch("games.taskGame.taskGame.TASKS", DUMMY_TASKS):
            with patch("builtins.input", side_effect=["", "q"]):
                game.playRound()

    def testEmptyTasksExitsEarly(self):
        """Game exits early and prints a message when no tasks are defined."""
        game = TaskGame(players=makePlayers("Testi Timo"))
        with patch("games.taskGame.taskGame.TASKS", []):
            with patch("builtins.print") as mockPrint:
                game.playRound()
                mockPrint.assert_any_call("No tasks defined.")

    def testGameEndEventFired(self):
        """GameEndEvent is emitted with correct player names."""
        from printing.log import GameLog
        log = GameLog()
        game = TaskGame(players=makePlayers("Testi Timo", "Testi Teppo"), log=log)
        with patch("games.taskGame.taskGame.TASKS", DUMMY_TASKS):
            with patch("builtins.input", side_effect=["", "q"]):
                game.playRound()
        endEvents = [e for e in log.events if isinstance(e, GameEndEvent)]
        self.assertEqual(len(endEvents), 1)
        names = [s["name"] for s in endEvents[0].scores]
        self.assertIn("Testi Timo", names)
        self.assertIn("Testi Teppo", names)

    def testResolveTargetsSingle(self):
        """players=1 targets the drawing player."""
        game = TaskGame(players=makePlayers("Testi Timo", "Testi Teppo"))
        drawer = game.players[0]
        targets = game._resolveTargets(1, drawer)
        self.assertEqual(targets, [drawer])

    def testResolveTargetsAll(self):
        """players='all' targets every player."""
        game = TaskGame(players=makePlayers("Testi Timo", "Testi Teppo", "Testi Matti"))
        targets = game._resolveTargets("all", game.players[0])
        self.assertEqual(len(targets), 3)

    def testResolveTargetsRandom(self):
        """players=2 picks 2 players excluding the drawer."""
        game = TaskGame(players=makePlayers("Testi Timo", "Testi Teppo", "Testi Matti"))
        drawer = game.players[0]
        targets = game._resolveTargets(2, drawer)
        self.assertEqual(len(targets), 2)
        self.assertNotIn(drawer, targets)


if __name__ == "__main__":
    unittest.main()
