import unittest
from printing.formatter import formatTurn, formatHand, formatBoardCard, formatTally, formatReceipt


class MockPrinter:
    def __init__(self):
        self.lines = []
        self.cuts = 0

    def set(self, **_): pass
    def textln(self, text=""): self.lines.append(str(text))
    def text(self, text=""): self.lines.append(str(text))
    def cut(self): self.cuts += 1


def makeTurn(player="Alice", guess="Red", card="♥A", correct=True,
             gave_to="Bob", drinks=1, note=None, hand_before=None):
    return {
        "player": player,
        "guess": guess,
        "card": card,
        "correct": correct,
        "gave_to": gave_to,
        "drinks": drinks,
        "note": note,
        "hand_before": hand_before or [],
    }


class TestFormatTurn(unittest.TestCase):

    def testShowsPlayerName(self):
        p = MockPrinter()
        formatTurn("Red or Black", makeTurn(player="Alice"), p)
        self.assertTrue(any("Alice" in l for l in p.lines))

    def testShowsGuess(self):
        p = MockPrinter()
        formatTurn("Red or Black", makeTurn(guess="Red"), p)
        self.assertTrue(any("Red" in l for l in p.lines))

    def testShowsCard(self):
        p = MockPrinter()
        formatTurn("Red or Black", makeTurn(card="♥A"), p)
        self.assertTrue(any("♥A" in l for l in p.lines))

    def testShowsGaveToOnCorrect(self):
        p = MockPrinter()
        formatTurn("Red or Black", makeTurn(gave_to="Bob", drinks=1), p)
        self.assertTrue(any("Bob" in l for l in p.lines))

    def testShowsDrinksOnWrong(self):
        p = MockPrinter()
        turn = makeTurn(gave_to=None, drinks=2, note=None)
        formatTurn("Red or Black", turn, p)
        self.assertTrue(any("2" in l for l in p.lines))

    def testShowsNoteWhenPresent(self):
        p = MockPrinter()
        turn = makeTurn(gave_to=None, drinks=2, note="on the line")
        formatTurn("Red or Black", turn, p)
        self.assertTrue(any("on the line" in l for l in p.lines))

    def testHigherOrLowerShowsBothCards(self):
        p = MockPrinter()
        turn = makeTurn(card="♥9", hand_before=["♥5"])
        formatTurn("Higher or Lower", turn, p)
        self.assertTrue(any("♥5" in l and "♥9" in l for l in p.lines))

    def testInsideOrOutsideShowsHand(self):
        p = MockPrinter()
        turn = makeTurn(hand_before=["♥3", "♥9"])
        formatTurn("Inside or Outside", turn, p)
        self.assertTrue(any("♥3" in l for l in p.lines))

    def testNoCutInsideTurn(self):
        p = MockPrinter()
        formatTurn("Red or Black", makeTurn(), p)
        self.assertEqual(p.cuts, 0)


class TestFormatHand(unittest.TestCase):

    def testShowsPlayerName(self):
        p = MockPrinter()
        formatHand("Alice", ["♥A", "♦K"], p)
        self.assertTrue(any("ALICE" in l for l in p.lines))

    def testShowsAllCardsSideBySide(self):
        p = MockPrinter()
        formatHand("Alice", ["♥A", "♦K", "♣Q"], p)
        self.assertTrue(any("♥A" in l and "♦K" in l and "♣Q" in l for l in p.lines))

    def testNoCut(self):
        p = MockPrinter()
        formatHand("Alice", ["♥A"], p)
        self.assertEqual(p.cuts, 0)


class TestFormatBoardCard(unittest.TestCase):

    def testShowsCard(self):
        p = MockPrinter()
        formatBoardCard({"card": "♥A", "action": "drink", "drinks": 2, "matched": [], "outcomes": []}, p)
        self.assertTrue(any("♥A" in l for l in p.lines))

    def testShowsNoMatchWhenEmpty(self):
        p = MockPrinter()
        formatBoardCard({"card": "♥A", "action": "drink", "drinks": 2, "matched": [], "outcomes": []}, p)
        self.assertTrue(any("No match" in l for l in p.lines))

    def testShowsDrinkOutcome(self):
        p = MockPrinter()
        card = {
            "card": "♥A", "action": "drink", "drinks": 4,
            "matched": ["Alice"],
            "outcomes": [{"type": "drink", "player": "Alice", "drinks": 4}],
        }
        formatBoardCard(card, p)
        self.assertTrue(any("Alice" in l and "4" in l for l in p.lines))

    def testShowsGiveOutcome(self):
        p = MockPrinter()
        card = {
            "card": "♥A", "action": "give", "drinks": 4,
            "matched": ["Alice"],
            "outcomes": [{"type": "give", "giver": "Alice", "receiver": "Bob", "drinks": 4}],
        }
        formatBoardCard(card, p)
        self.assertTrue(any("Alice" in l and "Bob" in l for l in p.lines))

    def testShowsShareOutcome(self):
        p = MockPrinter()
        card = {
            "card": "♥A", "action": "share", "drinks": 4,
            "matched": ["Alice"],
            "outcomes": [{"type": "share", "player1": "Alice", "player2": "Bob", "drinks": 4}],
        }
        formatBoardCard(card, p)
        self.assertTrue(any("Alice" in l and "Bob" in l for l in p.lines))


class TestFormatTally(unittest.TestCase):

    def testShowsEachPlayer(self):
        p = MockPrinter()
        formatTally([{"name": "Alice", "drank": 5, "gave": 3}, {"name": "Bob", "drank": 2, "gave": 7}], p)
        self.assertTrue(any("Alice" in l for l in p.lines))
        self.assertTrue(any("Bob" in l for l in p.lines))

    def testShowsDrankAndGave(self):
        p = MockPrinter()
        formatTally([{"name": "Alice", "drank": 5, "gave": 3}], p)
        self.assertTrue(any("5" in l and "3" in l for l in p.lines))


class TestFormatReceipt(unittest.TestCase):

    def testCutsAfterEachTurn(self):
        p = MockPrinter()
        data = {
            "phases": [{"name": "Red or Black", "turns": [makeTurn(), makeTurn(player="Bob")]}],
            "hands": {},
            "board": [],
            "scores": [],
        }
        formatReceipt(data, p)
        self.assertEqual(p.cuts, 2)

    def testCutsAfterEachHand(self):
        p = MockPrinter()
        data = {
            "phases": [],
            "hands": {"Alice": ["♥A"], "Bob": ["♦K"]},
            "board": [],
            "scores": [],
        }
        formatReceipt(data, p)
        self.assertEqual(p.cuts, 2)

    def testCutsAfterEachBoardCard(self):
        p = MockPrinter()
        card = {"card": "♥A", "action": "drink", "drinks": 2, "matched": [], "outcomes": []}
        data = {"phases": [], "hands": {}, "board": [card, card], "scores": []}
        formatReceipt(data, p)
        self.assertEqual(p.cuts, 2)


if __name__ == "__main__":
    unittest.main()
