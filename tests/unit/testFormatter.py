import unittest
from printing.receipts.bujaFormatter import formatTurn, formatHand, formatBoardCard, formatTally, formatReceipt, formatRouletteResult
from printing.receipts.ravitFormatter import formatRaceEvents, formatRaceTrack, formatRavitWinner, formatBettorDrink, formatJockeyList, formatTiebreakStart, formatTiebreakRound
from printing.receipts.taskGameFormatter import formatTaskDraw
from printing.receipts.diceFormatter import formatChallenge as formatMexicoChallenge, formatTally as formatMexicoTally
from core.events import TaskDrawEvent, RouletteResultEvent, RaceRoundEvent, RavitBettorDrinkEvent, TiebreakStartEvent, TiebreakRoundEvent
from games.diceGame.diceEvents import MexicanChallengeEvent
from tests.testUtils import SilentTest

class MockPrinter:
    def __init__(self):
        self.lines = []
        self.cuts = 0

    def set(self, **_): pass
    def textln(self, text=""): self.lines.append(str(text))
    def text(self, text=""): self.lines.append(str(text))
    def cut(self): self.cuts += 1

def makeTurn(player="Testi Matti", guess="Red", card="❤︎⁠A", correct=True,
             gaveTo="Testi Timo", drinks=1, note=None, handBefore=None):
    return {
        "player": player,
        "guess": guess,
        "card": card,
        "correct": correct,
        "gaveTo": gaveTo,
        "drinks": drinks,
        "note": note,
        "handBefore": handBefore or [],
    }

class TestFormatTurn(SilentTest):

    def testShowsPlayerName(self):
        p = MockPrinter()
        formatTurn("Red or Black", makeTurn(player="Testi Matti"), p)
        self.assertTrue(any("Testi Matti" in line for line in p.lines))

    def testShowsGuess(self):
        p = MockPrinter()
        formatTurn("Red or Black", makeTurn(guess="Red"), p)
        self.assertTrue(any("Red" in line for line in p.lines))

    def testShowsCard(self):
        p = MockPrinter()
        formatTurn("Red or Black", makeTurn(card="❤︎⁠A"), p)
        self.assertTrue(any("❤︎⁠A" in line for line in p.lines))

    def testShowsGaveToOnCorrect(self):
        p = MockPrinter()
        formatTurn("Red or Black", makeTurn(gaveTo="Testi Timo", drinks=1), p)
        self.assertTrue(any("Testi Timo" in line for line in p.lines))

    def testShowsDrinksOnWrong(self):
        p = MockPrinter()
        turn = makeTurn(gaveTo=None, drinks=2, note=None, correct=False)
        formatTurn("Red or Black", turn, p)
        self.assertTrue(any("2" in line for line in p.lines))

    def testShowsNoteWhenPresent(self):
        p = MockPrinter()
        turn = makeTurn(gaveTo=None, drinks=2, note="on the line", correct=None)
        formatTurn("Red or Black", turn, p)
        self.assertTrue(any("on the line" in line for line in p.lines))

    def testHigherOrLowerShowsBothCards(self):
        p = MockPrinter()
        turn = makeTurn(card="❤︎⁠9", handBefore=["❤︎⁠5"])
        formatTurn("Isompi vai pienempi?", turn, p)
        self.assertTrue(any("❤︎⁠5" in line and "❤︎⁠9" in line for line in p.lines))

    def testInsideOrOutsideShowsHand(self):
        p = MockPrinter()
        turn = makeTurn(handBefore=["❤︎⁠3", "❤︎⁠9"])
        formatTurn("Välistä vai ulkoa?", turn, p)
        self.assertTrue(any("❤︎⁠3" in line for line in p.lines))

    def testNoCutInsideTurn(self):
        p = MockPrinter()
        formatTurn("Red or Black", makeTurn(), p)
        self.assertEqual(p.cuts, 0)

class TestFormatHand(SilentTest):

    def testShowsPlayerName(self):
        p = MockPrinter()
        formatHand("Testi Matti", ["❤︎⁠A", "♦K"], p)
        self.assertTrue(any("TESTI MATTI" in line for line in p.lines))

    def testShowsAllCardsSideBySide(self):
        p = MockPrinter()
        formatHand("Testi Matti", ["❤︎⁠A", "♦K", "♣Q"], p)
        self.assertTrue(any("❤︎⁠A" in line and "♦K" in line and "♣Q" in line for line in p.lines))

    def testNoCut(self):
        p = MockPrinter()
        formatHand("Testi Matti", ["❤︎⁠A"], p)
        self.assertEqual(p.cuts, 0)

class TestFormatBoardCard(SilentTest):

    def testShowsCard(self):
        p = MockPrinter()
        formatBoardCard({"card": "❤︎⁠A", "action": "drink", "drinks": 2, "matched": [], "outcomes": []}, p)
        self.assertTrue(any("❤︎⁠A" in line for line in p.lines))

    def testShowsNoMatchWhenEmpty(self):
        p = MockPrinter()
        formatBoardCard({"card": "❤︎⁠A", "action": "drink", "drinks": 2, "matched": [], "outcomes": []}, p)
        self.assertTrue(any("Ei osumia" in line for line in p.lines))

    def testShowsDrinkOutcome(self):
        p = MockPrinter()
        card = {
            "card": "❤︎⁠A", "action": "drink", "drinks": 4,
            "matched": ["Testi Matti"],
            "outcomes": [{"type": "drink", "player": "Testi Matti", "drinks": 4}],
        }
        formatBoardCard(card, p)
        self.assertTrue(any("Testi Matti" in line and "4" in line for line in p.lines))

    def testShowsGiveOutcome(self):
        p = MockPrinter()
        card = {
            "card": "❤︎⁠A", "action": "give", "drinks": 4,
            "matched": ["Testi Matti"],
            "outcomes": [{"type": "give", "giver": "Testi Matti", "receiver": "Testi Timo", "drinks": 4}],
        }
        formatBoardCard(card, p)
        self.assertTrue(any("Testi Matti" in line and "Testi Timo" in line for line in p.lines))

    def testShowsShareOutcome(self):
        p = MockPrinter()
        card = {
            "card": "❤︎⁠A", "action": "share", "drinks": 4,
            "matched": ["Testi Matti"],
            "outcomes": [{"type": "share", "player1": "Testi Matti", "player2": "Testi Timo", "drinks": 4}],
        }
        formatBoardCard(card, p)
        self.assertTrue(any("Testi Matti" in line and "Testi Timo" in line for line in p.lines))

class TestFormatTally(SilentTest):

    def testShowsEachPlayer(self):
        p = MockPrinter()
        formatTally([{"name": "Testi Matti", "drank": 5, "gave": 3}, {"name": "Testi Timo", "drank": 2, "gave": 7}], p)
        self.assertTrue(any("Testi Matti" in line for line in p.lines))
        self.assertTrue(any("Testi Timo" in line for line in p.lines))

    def testShowsDrankAndGave(self):
        p = MockPrinter()
        formatTally([{"name": "Testi Matti", "drank": 5, "gave": 3}], p)
        self.assertTrue(any("5" in line and "3" in line for line in p.lines))

class TestFormatReceipt(SilentTest):

    def testCutsAfterEachTurn(self):
        p = MockPrinter()
        data = {
            "phases": [{"name": "Red or Black", "turns": [makeTurn(), makeTurn(player="Testi Timo")]}],
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
            "hands": {"Testi Matti": ["❤︎⁠A"], "Testi Timo": ["♦K"]},
            "board": [],
            "scores": [],
        }
        formatReceipt(data, p)
        self.assertEqual(p.cuts, 2)

    def testCutsAfterEachBoardCard(self):
        p = MockPrinter()
        card = {"card": "❤︎⁠A", "action": "drink", "drinks": 2, "matched": [], "outcomes": []}
        data = {"phases": [], "hands": {}, "board": [card, card], "scores": []}
        formatReceipt(data, p)
        self.assertEqual(p.cuts, 2)

class TestFormatTaskDraw(SilentTest):

    def testShowsTitle(self):
        p = MockPrinter()
        formatTaskDraw(TaskDrawEvent(drawer="Teppo", title="Luuppi", description="Huuda luuppi.", targets=["Teppo"]), p)
        self.assertTrue(any("LUUPPI" in line for line in p.lines))

    def testShowsAllTargets(self):
        p = MockPrinter()
        formatTaskDraw(TaskDrawEvent(drawer="Teppo", title="Pari", description="...", targets=["Teppo", "Matti"]), p)
        self.assertTrue(any("Teppo" in line and "Matti" in line for line in p.lines))

    def testShowsDescription(self):
        p = MockPrinter()
        formatTaskDraw(TaskDrawEvent(drawer="Teppo", title="X", description="Do something.", targets=["Teppo"]), p)
        self.assertTrue(any("Do something." in line for line in p.lines))


class TestFormatRouletteResult(SilentTest):

    def testShowsPlayerName(self):
        p = MockPrinter()
        formatRouletteResult(RouletteResultEvent(player="Teppo", hit=False, drinks=10), p)
        self.assertTrue(any("TEPPO" in line for line in p.lines))

    def testShowsOsumaOnHit(self):
        p = MockPrinter()
        formatRouletteResult(RouletteResultEvent(player="Teppo", hit=True, drinks=10), p)
        self.assertTrue(any("OSUMA!" in line for line in p.lines))

    def testShowsDrinksOnHit(self):
        p = MockPrinter()
        formatRouletteResult(RouletteResultEvent(player="Teppo", hit=True, drinks=10), p)
        self.assertTrue(any("10" in line for line in p.lines))

    def testShowsOhiOnMiss(self):
        p = MockPrinter()
        formatRouletteResult(RouletteResultEvent(player="Teppo", hit=False, drinks=10), p)
        self.assertTrue(any("OHI!" in line for line in p.lines))

    def testNoOsumaOnMiss(self):
        p = MockPrinter()
        formatRouletteResult(RouletteResultEvent(player="Teppo", hit=False, drinks=10), p)
        self.assertFalse(any("OSUMA!" in line for line in p.lines))


class TestFormatRaceRoundEvents(SilentTest):
    def _makeEvent(self, raceEvents):
        positions = [{"name": "Ukko", "status": "racing", "position": 10}]
        return RaceRoundEvent(roundNumber=1, trackLength=20, positions=positions, raceEvents=raceEvents)

    def testEventsAndTrackPrintedSeparately(self):
        event = self._makeEvent([{"detail": "Salama iski!"}])
        pe = MockPrinter()
        formatRaceEvents(event, pe)
        pt = MockPrinter()
        formatRaceTrack(event, pt)
        self.assertTrue(any("Salama iski!" in line for line in pe.lines))
        self.assertFalse(any("Salama iski!" in line for line in pt.lines))
        self.assertTrue(any("Ukko" in line for line in pt.lines))
        self.assertFalse(any("Ukko" in line for line in pe.lines))

    def testTrackHasTwoSeparatorsWhenNoEvents(self):
        event = self._makeEvent([])
        p = MockPrinter()
        formatRaceTrack(event, p)
        separators = [line for line in p.lines if set(line.strip()) == {"="}]
        self.assertEqual(len(separators), 2)

    def testEventTextPrinted(self):
        p = MockPrinter()
        event = self._makeEvent([{"detail": "Hevonen kaatui!"}])
        formatRaceEvents(event, p)
        self.assertTrue(any("Hevonen kaatui!" in line for line in p.lines))


class TestFormatRavitWinner(SilentTest):
    def _makeData(self, bettors=None):
        return {
            "horseName": "Ukko",
            "odds": 1.3,
            "bettors": bettors if bettors is not None else [{"player": "Testi Tatti", "amount": 3}],
        }

    def testHorseNameShown(self):
        p = MockPrinter()
        formatRavitWinner(self._makeData(), p)
        self.assertTrue(any("UKKO" in line for line in p.lines))

    def testOddsShown(self):
        p = MockPrinter()
        formatRavitWinner(self._makeData(), p)
        self.assertTrue(any("1.3" in line for line in p.lines))

    def testBettorNameAndAmountShown(self):
        p = MockPrinter()
        formatRavitWinner(self._makeData(), p)
        self.assertTrue(any("Testi Tatti" in line for line in p.lines))
        self.assertTrue(any("3" in line for line in p.lines))

    def testNoBettorSeparatorWhenNoBettors(self):
        p = MockPrinter()
        formatRavitWinner(self._makeData(bettors=[]), p)
        separators = [line for line in p.lines if set(line.strip()) == {"-"}]
        self.assertEqual(len(separators), 0)

    def testMultipleBettorsAllShown(self):
        p = MockPrinter()
        data = self._makeData(bettors=[
            {"player": "Testi Tatti", "amount": 3},
            {"player": "Testi Matti", "amount": 1},
        ])
        formatRavitWinner(data, p)
        self.assertTrue(any("Testi Tatti" in line for line in p.lines))
        self.assertTrue(any("Testi Matti" in line for line in p.lines))


class TestFormatBettorDrink(SilentTest):
    def _makeEvent(self):
        return RavitBettorDrinkEvent(
            playerName="Testi",
            horseName="Ukko",
            amount=2,
            reason="hevonen kompuroi",
            scores=[{"name": "Testi", "drank": 2}, {"name": "Matti", "drank": 0}],
        )

    def testDrinkerNameShown(self):
        p = MockPrinter()
        formatBettorDrink(self._makeEvent(), p)
        self.assertTrue(any("Testi" in line for line in p.lines))

    def testNonDrinkerNotShown(self):
        p = MockPrinter()
        formatBettorDrink(self._makeEvent(), p)
        self.assertFalse(any("Matti" in line for line in p.lines))

    def testAmountAndHorseShown(self):
        p = MockPrinter()
        formatBettorDrink(self._makeEvent(), p)
        self.assertTrue(any("2" in line for line in p.lines))
        self.assertTrue(any("Ukko" in line for line in p.lines))


class TestFormatJockeyList(SilentTest):
    def testDescriptionShown(self):
        p = MockPrinter()
        jockeys = [{"horseName": "Ukko", "jockeyName": "Turbo", "jockeyDescription": "+1 nopeus"}]
        formatJockeyList(jockeys, p)
        self.assertTrue(any("+1 nopeus" in line for line in p.lines))

    def testNameShown(self):
        p = MockPrinter()
        jockeys = [{"horseName": "Ukko", "jockeyName": "Turbo", "jockeyDescription": "+1 nopeus"}]
        formatJockeyList(jockeys, p)
        self.assertTrue(any("Turbo" in line for line in p.lines))

    def testHorseNameShown(self):
        p = MockPrinter()
        jockeys = [{"horseName": "Ukko", "jockeyName": "Turbo", "jockeyDescription": "desc"}]
        formatJockeyList(jockeys, p)
        self.assertTrue(any("Ukko" in line for line in p.lines))


class TestTiebreakDisplay(SilentTest):
    def _startEvent(self):
        return TiebreakStartEvent(combatants=[
            {"id": 1, "name": "Ukko", "odds": 2.0, "health": 20, "maxHealth": 20, "strength": 4},
        ])

    def _roundEvent(self, health=20):
        return TiebreakRoundEvent(roundNumber=1, combatants=[
            {"name": "Ukko", "health": health, "maxHealth": 20, "strength": 4},
        ])

    def testNoVColonInTiebreakStart(self):
        p = MockPrinter()
        formatTiebreakStart(self._startEvent(), p)
        self.assertFalse(any("v:" in line for line in p.lines))

    def testNoVColonInTiebreakRound(self):
        p = MockPrinter()
        formatTiebreakRound(self._roundEvent(), p)
        self.assertFalse(any("v:" in line for line in p.lines))

    def testHealthbarIsWiderThanSix(self):
        p = MockPrinter()
        formatTiebreakRound(self._roundEvent(), p)
        bar_line = next(line for line in p.lines if "Ukko" in line and "[" in line)
        bar = bar_line[bar_line.index("[") + 1: bar_line.index("]")]
        self.assertGreater(len(bar), 6)


class TestFormatMexicoChallenge(SilentTest):

    def _makeEvent(self, wasMexico=False, loser="Testi Tatti", claimer="Testi Tatti", challenger="Testi Matti"):
        return MexicanChallengeEvent(
            challenger=challenger,
            claimer=claimer,
            claimed=1000 if wasMexico else 65,
            actual=43,
            d1=4,
            d2=3,
            loser=loser,
            drinks=2 if wasMexico else 1,
            wasMexico=wasMexico,
        )

    def testShowsClaimer(self):
        p = MockPrinter()
        formatMexicoChallenge(self._makeEvent(), p)
        self.assertTrue(any("Testi Tatti" in line for line in p.lines))

    def testShowsChallenger(self):
        p = MockPrinter()
        formatMexicoChallenge(self._makeEvent(), p)
        self.assertTrue(any("Testi Matti" in line for line in p.lines))

    def testShowsVerdictClaimerLied(self):
        p = MockPrinter()
        formatMexicoChallenge(self._makeEvent(loser="Testi Tatti", claimer="Testi Tatti"), p)
        self.assertTrue(any("VALEHTELI" in line for line in p.lines))

    def testShowsVerdictChallengerWrong(self):
        p = MockPrinter()
        formatMexicoChallenge(self._makeEvent(loser="Testi Matti", challenger="Testi Matti"), p)
        self.assertTrue(any("TURHAAN" in line for line in p.lines))

    def testShowsDrinkAmount(self):
        p = MockPrinter()
        formatMexicoChallenge(self._makeEvent(), p)
        self.assertTrue(any("1" in line for line in p.lines))

    def testMexicoLabelWhenWasMexico(self):
        p = MockPrinter()
        formatMexicoChallenge(self._makeEvent(wasMexico=True), p)
        self.assertTrue(any("MEXICO" in line for line in p.lines))

    def testNoMexicoLabelWhenNotMexico(self):
        p = MockPrinter()
        formatMexicoChallenge(self._makeEvent(wasMexico=False), p)
        labels = [line for line in p.lines if line.strip() == "MEXICO!"]
        self.assertEqual(len(labels), 0)


class TestFormatMexicoTally(SilentTest):

    def testShowsAllPlayers(self):
        p = MockPrinter()
        scores = [{"name": "Testi Tatti", "drank": 3, "gave": 0}, {"name": "Testi Matti", "drank": 1, "gave": 0}]
        formatMexicoTally(scores, p)
        self.assertTrue(any("Testi Tatti" in line for line in p.lines))
        self.assertTrue(any("Testi Matti" in line for line in p.lines))

    def testShowsDrinkCounts(self):
        p = MockPrinter()
        scores = [{"name": "Testi Tatti", "drank": 5, "gave": 0}]
        formatMexicoTally(scores, p)
        self.assertTrue(any("5" in line for line in p.lines))

    def testNoCut(self):
        p = MockPrinter()
        formatMexicoTally([{"name": "X", "drank": 1, "gave": 0}], p)
        self.assertEqual(p.cuts, 0)


if __name__ == "__main__":
    unittest.main()
