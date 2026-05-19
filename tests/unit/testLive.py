import unittest
from unittest.mock import MagicMock, patch
from core.events import (
    GameStartEvent, PhaseEvent, GuessEvent,
    DrinkEvent, GiveEvent, ShareEvent,
    BoardCardEvent, BoardCardDoneEvent, GameEndEvent,
    TaskDrawEvent, RouletteResultEvent,
)
from printing.log import GameLog
from printing.live import LivePrinter

def makeLog():
    log = GameLog()
    log.add(GameStartEvent(["Testi Matti", "Testi Timo"]))
    return log


def addPhaseTurn(log, phase, player, card="♥A", guess="Red", correct=True, gaveTo="Testi Timo", drinks=1):
    log.add(PhaseEvent(phase, player))
    log.add(GuessEvent(player, phase, guess, card, correct))
    if gaveTo:
        log.add(GiveEvent(player, gaveTo, drinks))
    else:
        log.add(DrinkEvent(player, drinks, "wrong guess"))

class TestLivePrinterPhase(unittest.TestCase):

    def testPrintsTurnAfterDrinkEvent(self):
        printer = MagicMock()
        log = makeLog()
        log.on(LivePrinter(printer).hook)

        addPhaseTurn(log, "Red or Black", "Testi Matti", correct=False, gaveTo=None, drinks=1)

        printer.printWith.assert_called_once()

    def testPrintsTurnAfterGiveEvent(self):
        printer = MagicMock()
        log = makeLog()
        log.on(LivePrinter(printer).hook)

        addPhaseTurn(log, "Red or Black", "Testi Matti", correct=True, gaveTo="Testi Timo", drinks=1)

        printer.printWith.assert_called_once()

    def testPrintsTurnPerPlayer(self):
        printer = MagicMock()
        log = makeLog()
        log.on(LivePrinter(printer).hook)

        addPhaseTurn(log, "Red or Black", "Testi Matti", gaveTo="Testi Timo")
        addPhaseTurn(log, "Red or Black", "Testi Timo", gaveTo="Testi Matti")

        self.assertEqual(printer.printWith.call_count, 2)

class TestLivePrinterHands(unittest.TestCase):

    def testPrintsHandsWhenBoardPhaseStarts(self):
        printer = MagicMock()
        log = makeLog()
        log.on(LivePrinter(printer).hook)

        addPhaseTurn(log, "Red or Black", "Testi Matti", gaveTo="Testi Timo")
        addPhaseTurn(log, "Red or Black", "Testi Timo", gaveTo="Testi Matti")
        log.add(PhaseEvent("Board", ""))

        # 2 turn receipts + 2 hand receipts
        self.assertEqual(printer.printWith.call_count, 4)

class TestLivePrinterBoard(unittest.TestCase):

    def testPrintsNoMatchCardImmediately(self):
        printer = MagicMock()
        log = makeLog()
        log.on(LivePrinter(printer).hook)

        log.add(PhaseEvent("Board", ""))
        log.add(BoardCardEvent("♥A", "drink", 2, []))
        log.add(BoardCardDoneEvent())

        # 2 hands + 1 board card
        self.assertEqual(printer.printWith.call_count, 3)

    def testMatchedCardPrintsAfterOutcomes(self):
        printer = MagicMock()
        log = makeLog()
        log.on(LivePrinter(printer).hook)

        log.add(PhaseEvent("Board", ""))
        log.add(BoardCardEvent("♥A", "drink", 2, ["Testi Matti"]))
        log.add(DrinkEvent("Testi Matti", 2, "board"))
        log.add(BoardCardDoneEvent())

        # 2 hands + 1 board card (with outcomes)
        self.assertEqual(printer.printWith.call_count, 3)

    def testPrintsLastBoardCardAndTallyAtGameEnd(self):
        printer = MagicMock()
        log = makeLog()
        log.on(LivePrinter(printer).hook)

        log.add(PhaseEvent("Board", ""))
        log.add(BoardCardEvent("♥A", "drink", 2, []))
        log.add(BoardCardDoneEvent())
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


class TestLivePrinterTaskGameEnd(unittest.TestCase):

    def testPrintsTaskGameReceiptOnGameEnd(self):
        printer = MagicMock()
        log = makeLog()
        log.on(LivePrinter(printer, gameTitle="TaskGame").hook)
        log.add(GameEndEvent(scores=[{"name": "Teppo", "drinksTaken": 3, "drinksToGive": 1}]))
        printer.printWith.assert_called_once()

    def testTaskGameEndDoesNotPrintBoardCard(self):
        printer = MagicMock()
        log = makeLog()
        log.on(LivePrinter(printer, gameTitle="TaskGame").hook)
        log.add(GameEndEvent(scores=[]))
        # Only 1 printWith call (the receipt), not 2 (board card + tally)
        self.assertEqual(printer.printWith.call_count, 1)

    def testBujaEndUsesReceipt(self):
        printer = MagicMock()
        log = makeLog()
        log.on(LivePrinter(printer, gameTitle="Buja").hook)
        log.add(PhaseEvent("Board", ""))
        log.add(GameEndEvent(scores=[{"name": "Teppo", "drinksTaken": 3, "drinksToGive": 1}]))
        # 2 hands + 1 consolidated receipt
        self.assertEqual(printer.printWith.call_count, 3)


class TestLivePrinterTaskGame(unittest.TestCase):

    def testPrintsOnTaskDraw(self):
        printer = MagicMock()
        log = makeLog()
        log.on(LivePrinter(printer).hook)
        log.add(TaskDrawEvent(drawer="Teppo", title="Luuppi", description="Huuda luuppi.", targets=["Teppo"]))
        printer.printWith.assert_called_once()

    def testPrintsOnRouletteResult(self):
        printer = MagicMock()
        log = makeLog()
        log.on(LivePrinter(printer).hook)
        log.add(RouletteResultEvent(player="Teppo", hit=True, drinks=10))
        printer.printWith.assert_called_once()

    def testPrintsPerRouletteResult(self):
        printer = MagicMock()
        log = makeLog()
        log.on(LivePrinter(printer).hook)
        log.add(RouletteResultEvent(player="Teppo", hit=False, drinks=10))
        log.add(RouletteResultEvent(player="Matti", hit=True, drinks=10))
        self.assertEqual(printer.printWith.call_count, 2)


if __name__ == "__main__":
    unittest.main()
