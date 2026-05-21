import unittest
from unittest.mock import patch
from core.player import Player
from core.events import GameEndEvent
from games.taskGame.taskGame import TaskGame
from tests.testUtils import SilentTest

DUMMY_TASKS = [
    {"title": "Test Task", "description": "Do something.", "players": 1, "drinks": None, "drinkType": "special", "rarity": "common"},
    {"title": "Pair Task", "description": "Do something together.", "players": 2, "drinks": None, "drinkType": "special", "rarity": "common"},
    {"title": "All Task", "description": "Everyone does something.", "players": "all", "drinks": None, "drinkType": "special", "rarity": "common"},
]


def makePlayers(*names):
    return [Player(i + 1, name) for i, name in enumerate(names)]


def makeTask(drinkType, drinks=None, title="Task", players=1, rarity="common"):
    return {"title": title, "description": "desc", "players": players, "drinks": drinks, "drinkType": drinkType, "rarity": rarity}


class TestTaskGameRuns(SilentTest):
    def testGameCompletes(self):
        game = TaskGame(players=makePlayers("Testi Timo", "Testi Teppo"))
        with patch("games.taskGame.taskGame.TASKS", DUMMY_TASKS):
            with patch("builtins.input", side_effect=["", "quit"]):
                game.playRound()

    def testEmptyTasksExitsEarly(self):
        game = TaskGame(players=makePlayers("Testi Timo"))
        with patch("games.taskGame.taskGame.TASKS", []):
            with patch("builtins.print") as mockPrint:
                game.playRound()
                mockPrint.assert_any_call("Ei tehtäviä määritelty.")

    def testGameEndEventFired(self):
        from printing.log import GameLog
        log = GameLog()
        game = TaskGame(players=makePlayers("Testi Timo", "Testi Teppo"), log=log)
        with patch("games.taskGame.taskGame.TASKS", DUMMY_TASKS):
            with patch("builtins.input", side_effect=["", "quit"]):
                game.playRound()
        endEvents = [e for e in log.events if isinstance(e, GameEndEvent)]
        self.assertEqual(len(endEvents), 1)
        names = [s["name"] for s in endEvents[0].scores]
        self.assertIn("Testi Timo", names)
        self.assertIn("Testi Teppo", names)

    def testResolveTargetsSingle(self):
        game = TaskGame(players=makePlayers("Testi Timo", "Testi Teppo"))
        drawer = game.players[0]
        self.assertEqual(game._resolveTargets(1, drawer), [drawer])

    def testResolveTargetsAll(self):
        game = TaskGame(players=makePlayers("Testi Timo", "Testi Teppo", "Testi Matti"))
        self.assertEqual(len(game._resolveTargets("all", game.players[0])), 3)

    def testResolveTargetsRandom(self):
        game = TaskGame(players=makePlayers("Testi Timo", "Testi Teppo", "Testi Matti"))
        drawer = game.players[0]
        targets = game._resolveTargets(2, drawer)
        self.assertEqual(len(targets), 2)
        self.assertNotIn(drawer, targets)


class TestDrinkTracking(SilentTest):
    def testTakeDrinks(self):
        game = TaskGame(players=makePlayers("Teppo", "Matti"))
        drawer = game.players[0]
        with patch("builtins.input", return_value=""):
            game._handlePostTask(makeTask("take", drinks=3), [drawer], drawer)
        self.assertEqual(drawer.getDrinksTaken(), 3)

    def testTakeCustomAmount(self):
        game = TaskGame(players=makePlayers("Teppo", "Matti"))
        drawer = game.players[0]
        with patch("builtins.input", return_value="5"):
            game._handlePostTask(makeTask("take", drinks=3), [drawer], drawer)
        self.assertEqual(drawer.getDrinksTaken(), 5)

    def testGiveDrinks(self):
        game = TaskGame(players=makePlayers("Teppo", "Matti"))
        drawer, receiver = game.players[0], game.players[1]
        with patch("builtins.input", return_value="Matti"), \
             patch("builtins.print"):
            game._handlePostTask(makeTask("give", drinks=3), [drawer], drawer)
            game._interactiveGivePhase()
        self.assertEqual(receiver.getDrinksTaken(), 3)
        self.assertEqual(drawer.drinksToGive, 3)

    def testGiveToSelfRejected(self):
        game = TaskGame(players=makePlayers("Teppo", "Matti"))
        drawer = game.players[0]
        with patch("builtins.input", return_value="Teppo"):
            game._handlePostTask(makeTask("give", drinks=3), [drawer], drawer)
        self.assertEqual(drawer.getDrinksTaken(), 0)
        self.assertEqual(drawer.drinksToGive, 0)

    def testGiveUnknownPlayerSkipped(self):
        game = TaskGame(players=makePlayers("Teppo", "Matti"))
        with patch("builtins.input", return_value="Pekka"):
            game._handlePostTask(makeTask("give", drinks=3), [game.players[0]], game.players[0])
        self.assertEqual(game.players[1].getDrinksTaken(), 0)

    def testSocialDrinks(self):
        game = TaskGame(players=makePlayers("Teppo", "Matti"))
        # numbered list: pick 1 (Teppo) → 2 drinks, pick 2 (Matti) → 1 drink, budget exhausted
        with patch("builtins.input", side_effect=["1", "2", "2", "1"]):
            game._handlePostTask(makeTask("social", drinks=3), list(game.players), game.players[0])
        self.assertEqual(game.players[0].getDrinksTaken(), 2)
        self.assertEqual(game.players[1].getDrinksTaken(), 1)

    def testSocialSkipOnEnter(self):
        game = TaskGame(players=makePlayers("Teppo", "Matti"))
        with patch("builtins.input", return_value=""):
            game._handlePostTask(makeTask("social", drinks=3), list(game.players), game.players[0])
        self.assertEqual(game.players[0].getDrinksTaken(), 0)
        self.assertEqual(game.players[1].getDrinksTaken(), 0)


class TestPlayerLinks(SilentTest):
    def testPairStored(self):
        game = TaskGame(players=makePlayers("Teppo", "Matti"))
        drawer, partner = game.players[0], game.players[1]
        with patch("builtins.input", return_value="Matti"):
            game._handlePostTask(makeTask("link", title="Pari", players=2), [partner], drawer)
        self.assertEqual(len(game.activePairs), 1)
        self.assertIn(drawer, game.activePairs[0])
        self.assertIn(partner, game.activePairs[0])

    def testPairReplacesPrevious(self):
        game = TaskGame(players=makePlayers("Teppo", "Matti", "Pekka"))
        p1, p2, p3 = game.players
        game.activePairs = [[p1, p2]]
        with patch("builtins.input", return_value="Pekka"):
            game._handlePostTask(makeTask("link", title="Pari", players=2), [p3], p1)
        self.assertEqual(len(game.activePairs), 1)
        self.assertIn(p3, game.activePairs[0])
        self.assertNotIn(p2, game.activePairs[0])

    def testPairPropagatesDrinks(self):
        game = TaskGame(players=makePlayers("Teppo", "Matti"))
        p1, p2 = game.players
        game.activePairs = [[p1, p2]]
        game._assignDrinks(p1, 4)
        self.assertEqual(p1.getDrinksTaken(), 4)
        self.assertEqual(p2.getDrinksTaken(), 4)

    def testPairPropagatesBothDirections(self):
        game = TaskGame(players=makePlayers("Teppo", "Matti"))
        p1, p2 = game.players
        game.activePairs = [[p1, p2]]
        game._assignDrinks(p2, 3)
        self.assertEqual(p1.getDrinksTaken(), 3)
        self.assertEqual(p2.getDrinksTaken(), 3)

    def testHuoraStored(self):
        game = TaskGame(players=makePlayers("Master", "Huora"))
        master, huora = game.players
        with patch("builtins.input", return_value="Huora"):
            game._handlePostTask(makeTask("link", title="Huora", players=2), [huora], master)
        self.assertEqual(len(game.activeHuoras), 1)

    def testHuoraDrinksWhenMasterDrinks(self):
        game = TaskGame(players=makePlayers("Master", "Huora"))
        master, huora = game.players
        game.activeHuoras = [[master, huora]]
        game._assignDrinks(master, 5)
        self.assertEqual(master.getDrinksTaken(), 5)
        self.assertEqual(huora.getDrinksTaken(), 5)

    def testHuoraDoesNotPropagateReverse(self):
        game = TaskGame(players=makePlayers("Master", "Huora"))
        master, huora = game.players
        game.activeHuoras = [[master, huora]]
        game._assignDrinks(huora, 3)
        self.assertEqual(huora.getDrinksTaken(), 3)
        self.assertEqual(master.getDrinksTaken(), 0)

    def testHuoraDuplicateRejected(self):
        game = TaskGame(players=makePlayers("Master", "Huora"))
        master, huora = game.players
        task = makeTask("link", title="Huora", players=2)
        with patch("builtins.input", side_effect=["Huora", "Huora"]):
            game._handlePostTask(task, [huora], master)
            game._handlePostTask(task, [huora], master)
        self.assertEqual(len(game.activeHuoras), 1)

    def testMultipleHuorasStack(self):
        game = TaskGame(players=makePlayers("Master", "H1", "H2"))
        master, h1, h2 = game.players
        game.activeHuoras = [[master, h1], [master, h2]]
        game._assignDrinks(master, 2)
        self.assertEqual(h1.getDrinksTaken(), 2)
        self.assertEqual(h2.getDrinksTaken(), 2)


class TestImmunity(SilentTest):
    def testImmunityGranted(self):
        game = TaskGame(players=makePlayers("Teppo"))
        drawer = game.players[0]
        game._handlePostTask(makeTask("special", title="Immunitetti"), [drawer], drawer)
        self.assertIn(drawer, game.immunePlayers)

    def testImmunityBlocksDrink(self):
        game = TaskGame(players=makePlayers("Teppo"))
        player = game.players[0]
        game.immunePlayers = [player]
        game._assignDrinks(player, 5)
        self.assertEqual(player.getDrinksTaken(), 0)

    def testImmunityConsumedAfterUse(self):
        game = TaskGame(players=makePlayers("Teppo"))
        player = game.players[0]
        game.immunePlayers = [player]
        game._assignDrinks(player, 5)
        self.assertNotIn(player, game.immunePlayers)

    def testImmunityOnlyBlocksOnce(self):
        game = TaskGame(players=makePlayers("Teppo"))
        player = game.players[0]
        game.immunePlayers = [player]
        game._assignDrinks(player, 5)
        game._assignDrinks(player, 3)
        self.assertEqual(player.getDrinksTaken(), 3)


class TestRoulette(SilentTest):
    def testHitPlayerDrinks(self):
        game = TaskGame(players=makePlayers("A", "B", "C"))
        task = makeTask("roulette", drinks=10, players="all")
        with patch("games.taskGame.taskGame.random.randint", return_value=1):
            with patch("builtins.input", side_effect=["", ""]):
                game._handlePostTask(task, list(game.players), game.players[0])
        self.assertEqual(game.players[1].getDrinksTaken(), 10)

    def testMissedPlayersDontDrink(self):
        game = TaskGame(players=makePlayers("A", "B", "C"))
        task = makeTask("roulette", drinks=10, players="all")
        with patch("games.taskGame.taskGame.random.randint", return_value=1):
            with patch("builtins.input", side_effect=["", ""]):
                game._handlePostTask(task, list(game.players), game.players[0])
        self.assertEqual(game.players[0].getDrinksTaken(), 0)
        self.assertEqual(game.players[2].getDrinksTaken(), 0)

    def testRouletteStopsAfterHit(self):
        game = TaskGame(players=makePlayers("A", "B", "C"))
        task = makeTask("roulette", drinks=10, players="all")
        with patch("games.taskGame.taskGame.random.randint", return_value=1):
            with patch("builtins.input", side_effect=["", ""]) as mockInput:
                game._handlePostTask(task, list(game.players), game.players[0])
        self.assertEqual(mockInput.call_count, 2)


class TestDoubleNext(SilentTest):
    def testTuplaSetsFlagAndClearsOnNextCard(self):
        game = TaskGame(players=makePlayers("Teppo"))
        game._handlePostTask(makeTask("special", title="Tupla"), [game.players[0]], game.players[0])
        self.assertTrue(game.doubleNext)
        with patch("builtins.input", return_value=""):
            game._handlePostTask(makeTask("take", drinks=3), [game.players[0]], game.players[0])
        self.assertFalse(game.doubleNext)

    def testTuplaDoublesDrinks(self):
        game = TaskGame(players=makePlayers("Teppo"))
        game.doubleNext = True
        with patch("builtins.input", return_value=""):
            game._handlePostTask(makeTask("take", drinks=3), [game.players[0]], game.players[0])
        self.assertEqual(game.players[0].getDrinksTaken(), 6)

    def testTuplaConsumedOnSpecialCard(self):
        game = TaskGame(players=makePlayers("Teppo"))
        game.doubleNext = True
        game._handlePostTask(makeTask("special", title="Säänto"), [game.players[0]], game.players[0])
        self.assertFalse(game.doubleNext)

    def testTuplaDoesNotDoubleNoneDrinks(self):
        game = TaskGame(players=makePlayers("Teppo", "Matti"))
        game.doubleNext = True
        with patch("builtins.input", return_value=""):
            game._handlePostTask(makeTask("social", drinks=None), list(game.players), game.players[0])
        self.assertFalse(game.doubleNext)


class TestDeckCommand(SilentTest):
    def testDeckCommandShowsCount(self):
        from printing.log import GameLog
        game = TaskGame(players=makePlayers("A"), log=GameLog(), config={"commonCount": 1, "specialCount": 1})
        with patch("games.taskGame.taskGame.TASKS", [makeTask("special", title="X", rarity="common")]):
            with patch("builtins.input", side_effect=["d", "", "", ""]):
                with patch("builtins.print") as mockPrint:
                    game.playRound()
        printed = [str(c) for c in mockPrint.call_args_list]
        self.assertTrue(any("Kortteja jäljellä" in c for c in printed))

    def testDeckCommandDoesNotDraw(self):
        from printing.log import GameLog
        from core.events import TaskDrawEvent
        log = GameLog()
        game = TaskGame(players=makePlayers("A"), log=log, config={"commonCount": 1, "specialCount": 1})
        with patch("games.taskGame.taskGame.TASKS", [makeTask("special", title="X", rarity="common")]):
            with patch("builtins.input", side_effect=["d", "", "", ""]):
                game.playRound()
        self.assertEqual(len([e for e in log.events if isinstance(e, TaskDrawEvent)]), 1)

    def testDeckCommandShowsTotalAndRemaining(self):
        tasks = [makeTask("special", title="X", rarity="common")]
        game = TaskGame(players=makePlayers("A"), config={"commonCount": 3, "specialCount": 1})
        with patch("games.taskGame.taskGame.TASKS", tasks):
            with patch("builtins.input", side_effect=["d", "", "", "d", "", "", "d", "", "", "d", "", ""]):
                with patch("builtins.print") as mockPrint:
                    game.playRound()
        printed = " ".join(str(c) for c in mockPrint.call_args_list)
        self.assertIn("3/3", printed)
        self.assertIn("2/3", printed)
        self.assertIn("1/3", printed)


class TestBuildPool(SilentTest):
    def testCommonAndSpecialCounts(self):
        tasks = [
            makeTask("special", title="Common", rarity="common"),
            makeTask("special", title="Special", rarity="special"),
        ]
        game = TaskGame(players=makePlayers("A"), config={"commonCount": 3, "specialCount": 1})
        with patch("games.taskGame.taskGame.TASKS", tasks):
            pool = game._buildPool()
        self.assertEqual(len(pool), 4)
        self.assertEqual(sum(1 for t in pool if t["title"] == "Common"), 3)
        self.assertEqual(sum(1 for t in pool if t["title"] == "Special"), 1)

    def testDefaultCounts(self):
        tasks = [
            makeTask("special", title="Common", rarity="common"),
            makeTask("special", title="Special", rarity="special"),
        ]
        game = TaskGame(players=makePlayers("A"))
        with patch("games.taskGame.taskGame.TASKS", tasks):
            pool = game._buildPool()
        self.assertEqual(len(pool), 6)

    def testUnknownRarityTreatedAsCommon(self):
        tasks = [makeTask("special", title="X", rarity="legendary")]
        game = TaskGame(players=makePlayers("A"), config={"commonCount": 3, "specialCount": 1})
        with patch("games.taskGame.taskGame.TASKS", tasks):
            pool = game._buildPool()
        self.assertEqual(len(pool), 3)

    def testDeckEndsGame(self):
        from printing.log import GameLog
        log = GameLog()
        task = makeTask("special", title="X", rarity="common")
        game = TaskGame(players=makePlayers("A"), log=log, config={"commonCount": 1, "specialCount": 1})
        with patch("games.taskGame.taskGame.TASKS", [task]):
            with patch("builtins.input", side_effect=["", "", ""]):
                game.playRound()
        endEvents = [e for e in log.events if isinstance(e, GameEndEvent)]
        self.assertEqual(len(endEvents), 1)


class TestHuoraChainPropagation(SilentTest):
    def testTwoHopHuoraChain(self):
        game = TaskGame(players=makePlayers("A", "B", "C"))
        a, b, c = game.players
        game.activeHuoras = [[a, b], [b, c]]
        game._assignDrinks(a, 3)
        self.assertEqual(a.getDrinksTaken(), 3)
        self.assertEqual(b.getDrinksTaken(), 3)
        self.assertEqual(c.getDrinksTaken(), 3)

    def testHuoraCircularNoDoubleCount(self):
        game = TaskGame(players=makePlayers("A", "B"))
        a, b = game.players
        game.activeHuoras = [[a, b], [b, a]]
        game._assignDrinks(a, 3)
        self.assertEqual(a.getDrinksTaken(), 3)
        self.assertEqual(b.getDrinksTaken(), 3)

    def testPairMemberHuoraDrinks(self):
        game = TaskGame(players=makePlayers("A", "B", "C"))
        a, b, c = game.players
        game.activePairs = [[a, b]]
        game.activeHuoras = [[b, c]]
        game._assignDrinks(a, 5)
        self.assertEqual(a.getDrinksTaken(), 5)
        self.assertEqual(b.getDrinksTaken(), 5)
        self.assertEqual(c.getDrinksTaken(), 5)

    def testPairNoBackPropagation(self):
        game = TaskGame(players=makePlayers("A", "B"))
        a, b = game.players
        game.activePairs = [[a, b]]
        game._assignDrinks(a, 4)
        self.assertEqual(a.getDrinksTaken(), 4)
        self.assertEqual(b.getDrinksTaken(), 4)

    def testHuoraChainWithPairNoBounceBack(self):
        game = TaskGame(players=makePlayers("A", "B", "C"))
        a, b, c = game.players
        game.activeHuoras = [[a, b]]
        game.activePairs = [[b, c]]
        game._assignDrinks(a, 2)
        self.assertEqual(a.getDrinksTaken(), 2)
        self.assertEqual(b.getDrinksTaken(), 2)
        self.assertEqual(c.getDrinksTaken(), 2)


class TestChainCard(SilentTest):
    def _chainTask(self, drinks=3):
        return makeTask("chain", drinks=drinks, title="Juo 3,6,9...")

    def testChainCardSetsChainStep(self):
        game = TaskGame(players=makePlayers("A", "B", "C"))
        game._handlePostTask(self._chainTask(), [game.players[0]], game.players[0])
        self.assertEqual(game.chainStep, 2)

    def testChainCardSetsStepsLeft(self):
        game = TaskGame(players=makePlayers("A", "B", "C"))
        game._handlePostTask(self._chainTask(), [game.players[0]], game.players[0])
        self.assertEqual(game.chainStepsLeft, 2)  # len(players) - 1

    def testChainDrawerDrinks(self):
        game = TaskGame(players=makePlayers("A", "B"))
        drawer = game.players[0]
        game._handlePostTask(self._chainTask(drinks=3), [drawer], drawer)
        self.assertEqual(drawer.getDrinksTaken(), 3)

    def testApplyChainFiresCorrectAmount(self):
        game = TaskGame(players=makePlayers("A", "B", "C"))
        game.chainStep = 2
        game.chainStepsLeft = 2
        game._applyChain(game.players[1])
        self.assertEqual(game.players[1].getDrinksTaken(), 6)

    def testApplyChainIncrementsStep(self):
        game = TaskGame(players=makePlayers("A", "B", "C"))
        game.chainStep = 2
        game.chainStepsLeft = 2
        game._applyChain(game.players[1])
        self.assertEqual(game.chainStep, 3)

    def testChainStopsWhenExhausted(self):
        game = TaskGame(players=makePlayers("A", "B"))
        game.chainStep = 2
        game.chainStepsLeft = 1
        game._applyChain(game.players[1])
        self.assertEqual(game.chainStep, 0)

    def testChainStepsLeftDecrement(self):
        game = TaskGame(players=makePlayers("A", "B", "C"))
        game.chainStep = 2
        game.chainStepsLeft = 3
        game._applyChain(game.players[1])
        self.assertEqual(game.chainStepsLeft, 2)

    def testChainEscalates(self):
        game = TaskGame(players=makePlayers("A", "B", "C"))
        a, b, c = game.players
        game._handlePostTask(self._chainTask(drinks=3), [a], a)
        game._applyChain(b)
        game._applyChain(c)
        self.assertEqual(a.getDrinksTaken(), 3)
        self.assertEqual(b.getDrinksTaken(), 6)
        self.assertEqual(c.getDrinksTaken(), 9)

    def testChainInactiveDoesNothing(self):
        game = TaskGame(players=makePlayers("A"))
        game._applyChain(game.players[0])
        self.assertEqual(game.players[0].getDrinksTaken(), 0)


class TestCalcChainAssignments(SilentTest):
    def testAssignmentCount(self):
        game = TaskGame(players=makePlayers("A", "B", "C"))
        result = game._calcChainAssignments(game.players[0], 3)
        self.assertEqual(len(result), 3)

    def testDrawerFirst(self):
        game = TaskGame(players=makePlayers("A", "B", "C"))
        result = game._calcChainAssignments(game.players[0], 3)
        self.assertEqual(result[0]["name"], "A")
        self.assertEqual(result[0]["amount"], 3)

    def testAmountsEscalate(self):
        game = TaskGame(players=makePlayers("A", "B", "C"))
        result = game._calcChainAssignments(game.players[0], 3)
        self.assertEqual(result[1]["amount"], 6)
        self.assertEqual(result[2]["amount"], 9)

    def testTurnOrderWraps(self):
        game = TaskGame(players=makePlayers("A", "B", "C"))
        result = game._calcChainAssignments(game.players[1], 3)  # B draws
        self.assertEqual(result[0]["name"], "B")
        self.assertEqual(result[1]["name"], "C")
        self.assertEqual(result[2]["name"], "A")

    def testCascadeIncluded(self):
        game = TaskGame(players=makePlayers("A", "B", "C"))
        a, b = game.players[0], game.players[1]
        game.activeHuoras = [[a, b]]
        result = game._calcChainAssignments(a, 3)
        cascadeNames = [entry["name"] for entry in result[0]["cascades"]]
        self.assertIn("B", cascadeNames)

    def testTraceCascadeDoesNotModifyState(self):
        game = TaskGame(players=makePlayers("A", "B"))
        a, b = game.players
        game.activeHuoras = [[a, b]]
        game._traceCascade(a, 5)
        self.assertEqual(a.getDrinksTaken(), 0)
        self.assertEqual(b.getDrinksTaken(), 0)

    def testTraceCascadeNoCycle(self):
        game = TaskGame(players=makePlayers("A", "B"))
        a, b = game.players
        game.activePairs = [[a, b]]
        result = game._traceCascade(a, 3)
        # Only B should appear once, not looped back to A
        names = [r["name"] for r in result]
        self.assertIn("B", names)
        self.assertNotIn("A", names)


class TestChainEventEmission(SilentTest):
    def testChainCardEmitsTaskChainStartEvent(self):
        from printing.log import GameLog
        from core.events import TaskChainStartEvent
        log = GameLog()
        game = TaskGame(players=makePlayers("A", "B"), log=log)
        task = makeTask("chain", drinks=3, title="Juo 3,6,9...", rarity="common")
        with patch("games.taskGame.taskGame.TASKS", [task]):
            with patch("builtins.input", side_effect=["", "quit"]):
                game.playRound()
        events = [e for e in log.events if isinstance(e, TaskChainStartEvent)]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].drawer, "A")

    def testChainCardDoesNotEmitTaskDrawEvent(self):
        from printing.log import GameLog
        from core.events import TaskDrawEvent
        log = GameLog()
        game = TaskGame(players=makePlayers("A", "B"), log=log)
        task = makeTask("chain", drinks=3, title="Juo 3,6,9...", rarity="common")
        with patch("games.taskGame.taskGame.TASKS", [task]):
            with patch("builtins.input", side_effect=["", "quit"]):
                game.playRound()
        self.assertEqual(len([e for e in log.events if isinstance(e, TaskDrawEvent)]), 0)

    def testNonChainCardEmitsTaskDrawEvent(self):
        from printing.log import GameLog
        from core.events import TaskDrawEvent
        log = GameLog()
        game = TaskGame(players=makePlayers("A"), log=log)
        task = makeTask("special", title="X", rarity="common")
        with patch("games.taskGame.taskGame.TASKS", [task]):
            with patch("builtins.input", side_effect=["", "quit"]):
                game.playRound()
        self.assertEqual(len([e for e in log.events if isinstance(e, TaskDrawEvent)]), 1)

    def testNonChainCardEmitsTallySummary(self):
        from printing.log import GameLog
        from core.events import TaskDrinkSummaryEvent
        log = GameLog()
        game = TaskGame(players=makePlayers("A"), log=log)
        task = makeTask("take", drinks=3, title="Juo 3", rarity="common")
        with patch("games.taskGame.taskGame.TASKS", [task]):
            with patch("builtins.input", side_effect=["", "", "quit"]):
                game.playRound()
        self.assertGreater(len([e for e in log.events if isinstance(e, TaskDrinkSummaryEvent)]), 0)

    def testChainCardDoesNotEmitTallySummary(self):
        from printing.log import GameLog
        from core.events import TaskDrinkSummaryEvent
        log = GameLog()
        game = TaskGame(players=makePlayers("A", "B"), log=log)
        task = makeTask("chain", drinks=3, title="Juo 3,6,9...", rarity="common")
        with patch("games.taskGame.taskGame.TASKS", [task]):
            with patch("builtins.input", side_effect=["", "quit"]):
                game.playRound()
        self.assertEqual(len([e for e in log.events if isinstance(e, TaskDrinkSummaryEvent)]), 0)

    def testChainStartEventHasAllAssignments(self):
        from printing.log import GameLog
        from core.events import TaskChainStartEvent
        log = GameLog()
        game = TaskGame(players=makePlayers("A", "B", "C"), log=log)
        task = makeTask("chain", drinks=3, title="Juo 3,6,9...", rarity="common")
        with patch("games.taskGame.taskGame.TASKS", [task]):
            with patch("builtins.input", side_effect=["", "quit"]):
                game.playRound()
        event = next(e for e in log.events if isinstance(e, TaskChainStartEvent))
        self.assertEqual(len(event.assignments), 3)
        amounts = [a["amount"] for a in event.assignments]
        self.assertEqual(amounts, [3, 6, 9])


class TestInteractiveLinkCard(SilentTest):
    def testPairCardPromptsForTarget(self):
        game = TaskGame(players=makePlayers("Teppo", "Matti"))
        with patch("builtins.input", return_value="Matti") as mock_input:
            game._handlePostTask(makeTask("link", title="Pari"), [game.players[0]], game.players[0])
        mock_input.assert_called()

    def testPairCardPickByNumber(self):
        game = TaskGame(players=makePlayers("Teppo", "Matti"))
        drawer, partner = game.players
        with patch("builtins.input", return_value="1"):
            game._handlePostTask(makeTask("link", title="Pari"), [drawer], drawer)
        self.assertIn(partner, game.activePairs[0])

    def testPairCardPickByName(self):
        game = TaskGame(players=makePlayers("Teppo", "Matti"))
        drawer, partner = game.players
        with patch("builtins.input", return_value="Matti"):
            game._handlePostTask(makeTask("link", title="Pari"), [drawer], drawer)
        self.assertIn(partner, game.activePairs[0])

    def testHuoraCardPickByNumber(self):
        game = TaskGame(players=makePlayers("Master", "Huora"))
        master, huora = game.players
        with patch("builtins.input", return_value="1"):
            game._handlePostTask(makeTask("link", title="Huora"), [master], master)
        self.assertEqual(len(game.activeHuoras), 1)
        self.assertIn(huora, game.activeHuoras[0])

    def testLinkCardRetryOnUnknown(self):
        game = TaskGame(players=makePlayers("Teppo", "Matti"))
        with patch("builtins.input", side_effect=["Pekka", "Matti"]):
            game._handlePostTask(makeTask("link", title="Pari"), [game.players[0]], game.players[0])
        self.assertEqual(len(game.activePairs), 1)


if __name__ == "__main__":
    unittest.main()
