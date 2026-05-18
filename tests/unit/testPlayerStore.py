import json
import os
import tempfile
import unittest
from datetime import datetime
from core.playerStore import PlayerStore
from core.events import DrinkEvent, GameEndEvent


def makeTempStore(initialData=None):
    """Create a PlayerStore backed by a temporary file."""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    if initialData is not None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(initialData, f)
    else:
        os.unlink(path)
    return PlayerStore(path=path, gameTitle="Buja")


def makeEndEvent(scores):
    """Create a GameEndEvent with a fixed timestamp."""
    event = GameEndEvent(scores=scores, timestamp=datetime(2026, 5, 19, 14, 32))
    return event


class TestPlayerStoreLoad(unittest.TestCase):
    def testLoadMissingFile(self):
        store = makeTempStore()
        self.assertEqual(store.data, {"players": {}, "sessions": []})

    def testLoadExistingFile(self):
        initial = {
            "players": {"Alice": {"gamesPlayed": 1, "totalDrinksTaken": 5, "totalDrinksGiven": 2}},
            "sessions": [],
        }
        store = makeTempStore(initialData=initial)
        self.assertEqual(store.data["players"]["Alice"]["gamesPlayed"], 1)


class TestPlayerStoreHook(unittest.TestCase):
    def testHookIgnoresNonGameEndEvent(self):
        store = makeTempStore()
        store.hook(DrinkEvent(player="Alice", amount=2, reason="wrong guess"), None)
        self.assertEqual(store.data["players"], {})
        self.assertEqual(store.data["sessions"], [])

    def testHookUpdatesPlayerTotals(self):
        store = makeTempStore()
        event = makeEndEvent([
            {"name": "Alice", "drinksTaken": 8, "drinksToGive": 3},
        ])
        store.hook(event, None)
        alice = store.data["players"]["Alice"]
        self.assertEqual(alice["gamesPlayed"], 1)
        self.assertEqual(alice["totalDrinksTaken"], 8)
        self.assertEqual(alice["totalDrinksGiven"], 3)

    def testHookAppendsSession(self):
        store = makeTempStore()
        event = makeEndEvent([{"name": "Alice", "drinksTaken": 8, "drinksToGive": 3}])
        store.hook(event, None)
        self.assertEqual(len(store.data["sessions"]), 1)
        session = store.data["sessions"][0]
        self.assertEqual(session["game"], "Buja")
        self.assertEqual(session["timestamp"], "2026-05-19 14:32")
        self.assertEqual(session["scores"][0]["name"], "Alice")

    def testHookAccumulatesAcrossGames(self):
        store = makeTempStore()
        event1 = makeEndEvent([{"name": "Alice", "drinksTaken": 8, "drinksToGive": 3}])
        event2 = makeEndEvent([{"name": "Alice", "drinksTaken": 4, "drinksToGive": 1}])
        store.hook(event1, None)
        store.hook(event2, None)
        alice = store.data["players"]["Alice"]
        self.assertEqual(alice["gamesPlayed"], 2)
        self.assertEqual(alice["totalDrinksTaken"], 12)
        self.assertEqual(alice["totalDrinksGiven"], 4)

    def testHookPersistsToDisk(self):
        store = makeTempStore()
        event = makeEndEvent([{"name": "Alice", "drinksTaken": 5, "drinksToGive": 1}])
        store.hook(event, None)
        with open(store.path, "r", encoding="utf-8") as f:
            saved = json.load(f)
        self.assertIn("Alice", saved["players"])


class TestPlayerStoreDelete(unittest.TestCase):
    def testDeletePlayer(self):
        store = makeTempStore()
        store.hook(makeEndEvent([{"name": "Alice", "drinksTaken": 5, "drinksToGive": 1}]), None)
        result = store.deletePlayer("Alice")
        self.assertTrue(result)
        self.assertNotIn("Alice", store.data["players"])

    def testDeletePlayerNotFound(self):
        store = makeTempStore()
        result = store.deletePlayer("Nobody")
        self.assertFalse(result)

    def testDeleteSession(self):
        store = makeTempStore()
        store.hook(makeEndEvent([{"name": "Alice", "drinksTaken": 5, "drinksToGive": 1}]), None)
        result = store.deleteSession(0)
        self.assertTrue(result)
        self.assertEqual(store.data["sessions"], [])

    def testDeleteSessionOutOfRange(self):
        store = makeTempStore()
        result = store.deleteSession(0)
        self.assertFalse(result)

    def testDeleteSessionOutOfRangeNegative(self):
        store = makeTempStore()
        store.hook(makeEndEvent([{"name": "Alice", "drinksTaken": 5, "drinksToGive": 1}]), None)
        result = store.deleteSession(-1)
        self.assertFalse(result)


class TestPlayerStoreLeaderboard(unittest.TestCase):
    def testGetLeaderboard(self):
        store = makeTempStore()
        store.hook(makeEndEvent([
            {"name": "Alice", "drinksTaken": 3, "drinksToGive": 1},
            {"name": "Bob", "drinksTaken": 10, "drinksToGive": 2},
            {"name": "Carol", "drinksTaken": 6, "drinksToGive": 3},
        ]), None)
        board = store.getLeaderboard()
        self.assertEqual(board[0]["name"], "Bob")
        self.assertEqual(board[1]["name"], "Carol")
        self.assertEqual(board[2]["name"], "Alice")

    def testGetLeaderboardEmpty(self):
        store = makeTempStore()
        self.assertEqual(store.getLeaderboard(), [])


if __name__ == "__main__":
    unittest.main()
