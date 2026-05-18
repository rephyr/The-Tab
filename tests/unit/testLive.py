import unittest
from unittest.mock import MagicMock, patch
from core.events import (
    GameStartEvent, PhaseEvent, GuessEvent,
    DrinkEvent, GiveEvent, ShareEvent,
    BoardCardEvent, GameEndEvent,
)
from printing.log import GameLog
from printing.live import LivePrinter

def makeLog():
    log = GameLog()
    log.add(GameStartEvent(["Testi Matti", "Testi Timo"]))
    return log


def addPhaseTurn(log, phase, player, card="♥A", guess="Red", correct=True, gave_to="Testi Timo", drinks=1):
    log.add(PhaseEvent(phase, player))
    log.add(GuessEvent(player, phase, guess, card, correct))
    if gave_to:
        log.add(GiveEvent(player, gave_to, drinks))
    else:
        log.add(DrinkEvent(player, drinks, "wrong guess"))

class TestLivePrinterPhase(unittest.TestCase):

    def testPrintsTurnAfterDrinkEvent(self):
        printer = MagicMock()
        log = makeLog()
        log.on(LivePrinter(printer).hook)

        addPhaseTurn(log, "Red or Black", "Testi Matti", correct=False, gave_to=None, drinks=1)

        printer.printWith.assert_called_once()

    def testPrintsTurnAfterGiveEvent(self):
        printer = MagicMock()
        log = makeLog()
        log.on(LivePrinter(printer).hook)

        addPhaseTurn(log, "Red or Black", "Testi Matti", correct=True, gave_to="Testi Timo", drinks=1)

        printer.printWith.assert_called_once()

    def testPrintsTurnPerPlayer(self):
        printer = MagicMock()
        log = makeLog()
        log.on(LivePrinter(printer).hook)

        addPhaseTurn(log, "Red or Black", "Testi Matti", gave_to="Testi Timo")
        addPhaseTurn(log, "Red or Black", "Testi Timo", gave_to="Testi Matti")

        self.assertEqual(printer.printWith.call_count, 2)

class TestLivePrinterHands(unittest.TestCase):

    def testPrintsHandsWhenBoardPhaseStarts(self):
        printer = MagicMock()
        log = makeLog()
        log.on(LivePrinter(printer).hook)

        addPhaseTurn(log, "Red or Black", "Testi Matti", gave_to="Testi Timo")
        addPhaseTurn(log, "Red or Black", "Testi Timo", gave_to="Testi Matti")
        log.add(PhaseEvent("Board", ""))

        # 2 turn receipts + 2 hand receipts
        self.assertEqual(printer.printWith.call_count, 4)

class TestLivePrinterBoard(unittest.TestCase):

    def testPrintsBoardCardWhenNextCardArrives(self):
        printer = MagicMock()
        log = makeLog()
        log.on(LivePrinter(printer).hook)

        log.add(PhaseEvent("Board", ""))   # prints 2 hands (Testi Matti + Testi Timo)
        log.add(BoardCardEvent("♥A", "drink", 2, []))
        log.add(BoardCardEvent("♦K", "give", 2, []))  # prints previous card

        # 2 hands + 1 board card
        self.assertEqual(printer.printWith.call_count, 3)

    def testPrintsLastBoardCardAndTallyAtGameEnd(self):
        printer = MagicMock()
        log = makeLog()
        log.on(LivePrinter(printer).hook)

        log.add(PhaseEvent("Board", ""))   # prints 2 hands (Testi Matti + Testi Timo)
        log.add(BoardCardEvent("♥A", "drink", 2, []))
        log.add(GameEndEvent([{"name": "Testi Matti", "drinksTaken": 1, "drinksToGive": 0}]))

        # 2 hands + 1 board card + 1 tally
        self.assertEqual(printer.printWith.call_count, 4)

    def testClosesAfterGameEnd(self):
        printer = MagicMock()
        log = makeLog()
        log.on(LivePrinter(printer).hook)

        log.add(PhaseEvent("Board", ""))
        log.add(GameEndEvent([]))

        printer.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
