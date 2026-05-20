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

    def testDeletePlayerRemovesTheirSessionScores(self):
        store = makeTempStore()
        store.hook(makeEndEvent([{"name": "Alice", "drinksTaken": 5, "drinksToGive": 1}]), None)
        store.deletePlayer("Alice")
        self.assertEqual(len(store.data["sessions"]), 0)

    def testDeletePlayerKeepsSessionsWithOtherPlayers(self):
        store = makeTempStore()
        store.hook(makeEndEvent([
            {"name": "Alice", "drinksTaken": 5, "drinksToGive": 1},
            {"name": "Bob", "drinksTaken": 3, "drinksToGive": 0},
        ]), None)
        store.deletePlayer("Alice")
        self.assertEqual(len(store.data["sessions"]), 1)
        self.assertNotIn("Alice", [s["name"] for s in store.data["sessions"][0]["scores"]])

    def testDeletePlayerRemovedFromGetAllPlayerNames(self):
        store = makeTempStore()
        store.hook(makeEndEvent([{"name": "Alice", "drinksTaken": 5, "drinksToGive": 1}]), None)
        store.deletePlayer("Alice")
        self.assertNotIn("Alice", store.getAllPlayerNames())

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

    def testGetLeaderboardIncludesSessionOnlyPlayers(self):
        initial = {
            "players": {},
            "sessions": [
                {
                    "id": "2026-05-19T14:32:00",
                    "game": "Buja",
                    "timestamp": "2026-05-19 14:32",
                    "scores": [
                        {"name": "Testi Timo", "drinksTaken": 7, "drinksGiven": 2},
                        {"name": "Testi Teppo", "drinksTaken": 3, "drinksGiven": 1},
                    ],
                }
            ],
        }
        store = makeTempStore(initialData=initial)
        board = store.getLeaderboard()
        self.assertEqual(len(board), 2)
        self.assertEqual(board[0]["name"], "Testi Timo")
        self.assertEqual(board[0]["totalDrinksTaken"], 7)
        self.assertEqual(board[1]["name"], "Testi Teppo")


class TestPlayerStoreDailyLeaderboard(unittest.TestCase):
    def testDailyLeaderboardFiltersToDate(self):
        initial = {
            "players": {},
            "sessions": [
                {
                    "id": "2026-05-20T10:00:00",
                    "game": "Buja",
                    "timestamp": "2026-05-20 10:00",
                    "scores": [{"name": "Alice", "drinksTaken": 5, "drinksGiven": 1}],
                },
                {
                    "id": "2026-05-19T10:00:00",
                    "game": "Buja",
                    "timestamp": "2026-05-19 10:00",
                    "scores": [{"name": "Bob", "drinksTaken": 10, "drinksGiven": 2}],
                },
            ],
        }
        store = makeTempStore(initialData=initial)
        board = store.getDailyLeaderboard("2026-05-20")
        self.assertEqual(len(board), 1)
        self.assertEqual(board[0]["name"], "Alice")

    def testDailyLeaderboardAggregatesMultipleSessions(self):
        initial = {
            "players": {},
            "sessions": [
                {
                    "id": "2026-05-20T10:00:00",
                    "game": "Buja",
                    "timestamp": "2026-05-20 10:00",
                    "scores": [{"name": "Alice", "drinksTaken": 3, "drinksGiven": 1}],
                },
                {
                    "id": "2026-05-20T14:00:00",
                    "game": "TaskGame",
                    "timestamp": "2026-05-20 14:00",
                    "scores": [{"name": "Alice", "drinksTaken": 5, "drinksGiven": 0}],
                },
            ],
        }
        store = makeTempStore(initialData=initial)
        board = store.getDailyLeaderboard("2026-05-20")
        self.assertEqual(len(board), 1)
        self.assertEqual(board[0]["totalDrinksTaken"], 8)
        self.assertEqual(board[0]["gamesPlayed"], 2)

    def testDailyLeaderboardEmptyWhenNoSessions(self):
        store = makeTempStore()
        self.assertEqual(store.getDailyLeaderboard("2026-05-20"), [])

    def testDailyLeaderboardSortedByDrinksTaken(self):
        initial = {
            "players": {},
            "sessions": [
                {
                    "id": "2026-05-20T10:00:00",
                    "game": "Buja",
                    "timestamp": "2026-05-20 10:00",
                    "scores": [
                        {"name": "Alice", "drinksTaken": 3, "drinksGiven": 0},
                        {"name": "Bob", "drinksTaken": 9, "drinksGiven": 0},
                    ],
                },
            ],
        }
        store = makeTempStore(initialData=initial)
        board = store.getDailyLeaderboard("2026-05-20")
        self.assertEqual(board[0]["name"], "Bob")
        self.assertEqual(board[1]["name"], "Alice")


class TestPlayerStoreNameNormalization(unittest.TestCase):
    def testCaseInsensitiveLookupMergesStats(self):
        store = makeTempStore()
        store.hook(makeEndEvent([{"name": "Emi", "drinksTaken": 5, "drinksToGive": 1}]), None)
        store.hook(makeEndEvent([{"name": "emi", "drinksTaken": 3, "drinksToGive": 2}]), None)
        board = store.getLeaderboard()
        self.assertEqual(len(board), 1)
        self.assertEqual(board[0]["totalDrinksTaken"], 8)

    def testNewNameStoredAsTitleCase(self):
        store = makeTempStore()
        store.hook(makeEndEvent([{"name": "jemi", "drinksTaken": 4, "drinksToGive": 0}]), None)
        self.assertIn("Jemi", store.data["players"])

    def testExistingCasingPreserved(self):
        store = makeTempStore()
        store.hook(makeEndEvent([{"name": "Emi", "drinksTaken": 3, "drinksToGive": 0}]), None)
        store.hook(makeEndEvent([{"name": "EMI", "drinksTaken": 2, "drinksToGive": 0}]), None)
        self.assertIn("Emi", store.data["players"])
        self.assertNotIn("EMI", store.data["players"])


if __name__ == "__main__":
    unittest.main()
