import unittest
from unittest.mock import patch, MagicMock
from cli import showDailyLeaderboard
from tests.testUtils import SilentTest


def makeStore(sessions=None, daily=None):
    """Return a mock PlayerStore for CLI tests."""
    store = MagicMock()
    store.getSessions.return_value = sessions or []
    store.getDailyLeaderboard.return_value = daily or []
    return store


def makeSessions(*dates):
    """Build minimal session dicts for the given date strings (YYYY-MM-DD)."""
    return [
        {
            "timestamp": f"{d} 12:00",
            "game": "Buja",
            "scores": [{"name": "Alice", "drinksTaken": 3, "drinksGiven": 1}],
        }
        for d in dates
    ]


class TestShowDailyLeaderboard(SilentTest):

    def testNoSessionsShowsMessage(self):
        store = makeStore(sessions=[])
        printed = []
        with patch("builtins.print", side_effect=lambda *a: printed.append(" ".join(str(x) for x in a))), \
             patch("builtins.input", return_value=""):
            showDailyLeaderboard(store)
        self.assertTrue(any("tallennettu" in line for line in printed))

    def testDatesShownAsNumberedList(self):
        store = makeStore(sessions=makeSessions("2026-05-20", "2026-05-19"))
        store.getDailyLeaderboard.return_value = [
            {"name": "Alice", "totalDrinksTaken": 3, "totalDrinksGiven": 1, "gamesPlayed": 1}
        ]
        printed = []
        with patch("builtins.print", side_effect=lambda *a: printed.append(" ".join(str(x) for x in a))), \
             patch("builtins.input", side_effect=["1", ""]):
            showDailyLeaderboard(store)
        combined = "\n".join(printed)
        self.assertIn("2026-05-20", combined)
        self.assertIn("2026-05-19", combined)

    def testDatesOrderedNewestFirst(self):
        store = makeStore(sessions=makeSessions("2026-05-19", "2026-05-21", "2026-05-20"))
        store.getDailyLeaderboard.return_value = [
            {"name": "Alice", "totalDrinksTaken": 3, "totalDrinksGiven": 1, "gamesPlayed": 1}
        ]
        printed = []
        with patch("builtins.print", side_effect=lambda *a: printed.append(" ".join(str(x) for x in a))), \
             patch("builtins.input", side_effect=["1", ""]):
            showDailyLeaderboard(store)
        date_lines = [line for line in printed if "2026-05-" in line and any(c.isdigit() for c in line)]
        dates_in_order = [line for line in date_lines if "2026-05-21" in line or "2026-05-20" in line or "2026-05-19" in line]
        first = next(line for line in dates_in_order if "2026-05-21" in line)
        last = next(line for line in dates_in_order if "2026-05-19" in line)
        self.assertLess(dates_in_order.index(first), dates_in_order.index(last))

    def testEmptyInputCancels(self):
        store = makeStore(sessions=makeSessions("2026-05-20"))
        with patch("builtins.print"), \
             patch("builtins.input", return_value=""):
            showDailyLeaderboard(store)
        store.getDailyLeaderboard.assert_not_called()

    def testInvalidNumberShowsError(self):
        store = makeStore(sessions=makeSessions("2026-05-20"))
        printed = []
        with patch("builtins.print", side_effect=lambda *a: printed.append(" ".join(str(x) for x in a))), \
             patch("builtins.input", return_value="99"):
            showDailyLeaderboard(store)
        self.assertTrue(any("Virheellinen" in line for line in printed))
        store.getDailyLeaderboard.assert_not_called()

    def testSelectingDateCallsLeaderboard(self):
        sessions = makeSessions("2026-05-20", "2026-05-19")
        store = makeStore(sessions=sessions)
        store.getDailyLeaderboard.return_value = [
            {"name": "Alice", "totalDrinksTaken": 5, "totalDrinksGiven": 2, "gamesPlayed": 1}
        ]
        with patch("builtins.print"), \
             patch("builtins.input", side_effect=["1", ""]):
            showDailyLeaderboard(store)
        store.getDailyLeaderboard.assert_called_once_with("2026-05-20")

    def testScoresShownAfterSelection(self):
        store = makeStore(sessions=makeSessions("2026-05-20"))
        store.getDailyLeaderboard.return_value = [
            {"name": "Alice", "totalDrinksTaken": 7, "totalDrinksGiven": 2, "gamesPlayed": 2}
        ]
        printed = []
        with patch("builtins.print", side_effect=lambda *a: printed.append(" ".join(str(x) for x in a))), \
             patch("builtins.input", side_effect=["1", ""]):
            showDailyLeaderboard(store)
        combined = "\n".join(printed)
        self.assertIn("Alice", combined)
        self.assertIn("7", combined)

    def testDuplicateDateOnlyListedOnce(self):
        sessions = makeSessions("2026-05-20", "2026-05-20")
        store = makeStore(sessions=sessions)
        store.getDailyLeaderboard.return_value = [
            {"name": "Alice", "totalDrinksTaken": 3, "totalDrinksGiven": 1, "gamesPlayed": 1}
        ]
        printed = []
        with patch("builtins.print", side_effect=lambda *a: printed.append(" ".join(str(x) for x in a))), \
             patch("builtins.input", side_effect=["1", ""]):
            showDailyLeaderboard(store)
        date_lines = [line for line in printed if "2026-05-20" in line and "1." in line]
        self.assertEqual(len(date_lines), 1)


if __name__ == "__main__":
    unittest.main()
