import unittest
from datetime import datetime
from printing.log import GameLog
from core.events import (
    GameStartEvent, PhaseEvent, GuessEvent,
    DrinkEvent, GiveEvent, ShareEvent,
    BoardCardEvent, GameEndEvent,
)

def makeLog(*events):
    log = GameLog()
    for e in events:
        log.add(e)
    return log

class TestGameLogBasics(unittest.TestCase):

    def test_add_stores_event(self):
        log = GameLog()
        e = DrinkEvent("Matti", 1, "wrong guess")
        log.add(e)
        self.assertIn(e, log.events)

    def test_clear_empties_events(self):
        log = makeLog(DrinkEvent("Matti", 1, "wrong guess"))
        log.clear()
        self.assertEqual(log.events, [])

class TestToDictEmpty(unittest.TestCase):

    def test_empty_log_returns_base_structure(self):
        data = GameLog().toDict()
        self.assertEqual(data["players"], [])
        self.assertEqual(data["timestamp"], "")
        self.assertEqual(data["phases"], [])
        self.assertEqual(data["board"], [])
        self.assertEqual(data["scores"], [])

class TestToDictGameStart(unittest.TestCase):

    def setUp(self):
        ts = datetime(2026, 5, 18, 21, 47)
        self.data = makeLog(
            GameStartEvent(players=["Matti", "Teppo"], timestamp=ts)
        ).toDict()

    def test_players(self):
        self.assertEqual(self.data["players"], ["Matti", "Teppo"])

    def test_timestamp(self):
        self.assertEqual(self.data["timestamp"], "2026-05-18 21:47")

class TestToDictCorrectGuess(unittest.TestCase):

    def setUp(self):
        self.data = makeLog(
            PhaseEvent("Red or Black", "Matti"),
            GuessEvent("Matti", "Red or Black", "Red", "2♥", True),
            GiveEvent("Matti", "Teppo", 1),
        ).toDict()

    def test_phase_created(self):
        self.assertEqual(len(self.data["phases"]), 1)
        self.assertEqual(self.data["phases"][0]["name"], "Red or Black")

    def test_turn_player(self):
        turn = self.data["phases"][0]["turns"][0]
        self.assertEqual(turn["player"], "Matti")

    def test_turn_guess(self):
        turn = self.data["phases"][0]["turns"][0]
        self.assertEqual(turn["guess"], "Red")
        self.assertEqual(turn["card"], "2♥")
        self.assertTrue(turn["correct"])

    def test_turn_gave_to(self):
        turn = self.data["phases"][0]["turns"][0]
        self.assertEqual(turn["gave_to"], "Teppo")
        self.assertEqual(turn["drinks"], 1)

class TestToDictWrongGuess(unittest.TestCase):

    def setUp(self):
        self.data = makeLog(
            PhaseEvent("Red or Black", "Matti"),
            GuessEvent("Matti", "Red or Black", "Red", "5♠", False),
            DrinkEvent("Matti", 1, "wrong guess"),
        ).toDict()

    def test_turn_correct_false(self):
        turn = self.data["phases"][0]["turns"][0]
        self.assertFalse(turn["correct"])

    def test_turn_drinks(self):
        turn = self.data["phases"][0]["turns"][0]
        self.assertEqual(turn["drinks"], 1)

    def test_turn_gave_to_is_none(self):
        turn = self.data["phases"][0]["turns"][0]
        self.assertIsNone(turn["gave_to"])

    def test_no_note_for_wrong_guess(self):
        turn = self.data["phases"][0]["turns"][0]
        self.assertIsNone(turn["note"])

class TestToDictEdgeCases(unittest.TestCase):

    def test_same_value_has_note(self):
        data = makeLog(
            PhaseEvent("Higher or Lower", "Matti"),
            DrinkEvent("Matti", 2, "same value"),
        ).toDict()
        turn = data["phases"][0]["turns"][0]
        self.assertEqual(turn["drinks"], 2)
        self.assertEqual(turn["note"], "same value")
        self.assertIsNone(turn["guess"])

    def test_on_the_line_has_note(self):
        data = makeLog(
            PhaseEvent("Inside or Outside", "Matti"),
            DrinkEvent("Matti", 2, "on the line"),
        ).toDict()
        turn = data["phases"][0]["turns"][0]
        self.assertEqual(turn["note"], "on the line")

class TestToDictMultiplePhases(unittest.TestCase):

    def setUp(self):
        self.data = makeLog(
            PhaseEvent("Red or Black", "Matti"),
            GuessEvent("Matti", "Red or Black", "Red", "2♥", True),
            GiveEvent("Matti", "Teppo", 1),
            PhaseEvent("Higher or Lower", "Matti"),
            GuessEvent("Matti", "Higher or Lower", "Higher", "K♠", False),
            DrinkEvent("Matti", 1, "wrong guess"),
        ).toDict()

    def test_two_phases(self):
        self.assertEqual(len(self.data["phases"]), 2)

    def test_phase_names(self):
        names = [p["name"] for p in self.data["phases"]]
        self.assertIn("Red or Black", names)
        self.assertIn("Higher or Lower", names)

    def test_one_turn_per_phase(self):
        for phase in self.data["phases"]:
            self.assertEqual(len(phase["turns"]), 1)

class TestToDictMultipleTurnsSamePhase(unittest.TestCase):

    def setUp(self):
        self.data = makeLog(
            PhaseEvent("Red or Black", "Matti"),
            GuessEvent("Matti", "Red or Black", "Red", "2♥", True),
            GiveEvent("Matti", "Teppo", 1),
            PhaseEvent("Red or Black", "Teppo"),
            GuessEvent("Teppo", "Red or Black", "Black", "7♦", False),
            DrinkEvent("Teppo", 1, "wrong guess"),
        ).toDict()

    def test_one_phase_two_turns(self):
        self.assertEqual(len(self.data["phases"]), 1)
        self.assertEqual(len(self.data["phases"][0]["turns"]), 2)

    def test_turn_players(self):
        turns = self.data["phases"][0]["turns"]
        self.assertEqual(turns[0]["player"], "Matti")
        self.assertEqual(turns[1]["player"], "Teppo")

class TestToDictBoard(unittest.TestCase):

    def test_board_drink(self):
        data = makeLog(
            PhaseEvent("Board", ""),
            BoardCardEvent("7♥", "drink", 2, ["Matti"]),
            DrinkEvent("Matti", 2, "board"),
        ).toDict()
        card = data["board"][0]
        self.assertEqual(card["card"], "7♥")
        self.assertEqual(card["action"], "drink")
        self.assertEqual(card["drinks"], 2)
        self.assertEqual(card["matched"], ["Matti"])
        self.assertEqual(card["outcomes"][0]["type"], "drink")
        self.assertEqual(card["outcomes"][0]["player"], "Matti")

    def test_board_give(self):
        data = makeLog(
            PhaseEvent("Board", ""),
            BoardCardEvent("K♠", "give", 4, ["Teppo"]),
            GiveEvent("Teppo", "Matti", 4),
        ).toDict()
        outcome = data["board"][0]["outcomes"][0]
        self.assertEqual(outcome["type"], "give")
        self.assertEqual(outcome["giver"], "Teppo")
        self.assertEqual(outcome["receiver"], "Matti")
        self.assertEqual(outcome["drinks"], 4)

    def test_board_share(self):
        data = makeLog(
            PhaseEvent("Board", ""),
            BoardCardEvent("Q♦", "share", 4, ["Matti"]),
            ShareEvent("Matti", "Teppo", 4),
        ).toDict()
        outcome = data["board"][0]["outcomes"][0]
        self.assertEqual(outcome["type"], "share")
        self.assertEqual(outcome["player1"], "Matti")
        self.assertEqual(outcome["player2"], "Teppo")

    def test_board_no_match(self):
        data = makeLog(
            PhaseEvent("Board", ""),
            BoardCardEvent("3♣", "drink", 2, []),
        ).toDict()
        card = data["board"][0]
        self.assertEqual(card["matched"], [])
        self.assertEqual(card["outcomes"], [])

    def test_multiple_board_cards(self):
        data = makeLog(
            PhaseEvent("Board", ""),
            BoardCardEvent("7♥", "drink", 2, ["Matti"]),
            DrinkEvent("Matti", 2, "board"),
            BoardCardEvent("K♠", "give", 4, ["Teppo"]),
            GiveEvent("Teppo", "Matti", 4),
        ).toDict()
        self.assertEqual(len(data["board"]), 2)
        self.assertEqual(data["board"][0]["card"], "7♥")
        self.assertEqual(data["board"][1]["card"], "K♠")

class TestToDictScores(unittest.TestCase):

    def test_scores_from_game_end(self):
        data = makeLog(
            GameEndEvent(scores=[
                {"name": "Matti", "drinksTaken": 3, "drinksToGive": 4},
                {"name": "Teppo", "drinksTaken": 5, "drinksToGive": 2},
            ])
        ).toDict()
        self.assertEqual(len(data["scores"]), 2)
        self.assertEqual(data["scores"][0]["name"], "Matti")
        self.assertEqual(data["scores"][0]["drank"], 3)
        self.assertEqual(data["scores"][0]["gave"], 4)
        self.assertEqual(data["scores"][1]["name"], "Teppo")

if __name__ == "__main__":
    unittest.main()
