import unittest
from unittest.mock import patch
from core.player import Player
from core.events import GameEndEvent
from games.taskGame.taskGame import TaskGame

DUMMY_TASKS = [
    {"title": "Test Task", "description": "Do something.", "players": 1, "drinks": None, "drinkType": "special", "rarity": "common"},
    {"title": "Pair Task", "description": "Do something together.", "players": 2, "drinks": None, "drinkType": "special", "rarity": "common"},
    {"title": "All Task", "description": "Everyone does something.", "players": "all", "drinks": None, "drinkType": "special", "rarity": "common"},
]


def makePlayers(*names):
    return [Player(i + 1, name) for i, name in enumerate(names)]


def makeTask(drinkType, drinks=None, title="Task", players=1, rarity="common"):
    return {"title": title, "description": "desc", "players": players, "drinks": drinks, "drinkType": drinkType, "rarity": rarity}


class TestTaskGameRuns(unittest.TestCase):
    def testGameCompletes(self):
        game = TaskGame(players=makePlayers("Testi Timo", "Testi Teppo"))
        with patch("games.taskGame.taskGame.TASKS", DUMMY_TASKS):
            with patch("builtins.input", side_effect=["", "q"]):
                game.playRound()

    def testEmptyTasksExitsEarly(self):
        game = TaskGame(players=makePlayers("Testi Timo"))
        with patch("games.taskGame.taskGame.TASKS", []):
            with patch("builtins.print") as mockPrint:
                game.playRound()
                mockPrint.assert_any_call("No tasks defined.")

    def testGameEndEventFired(self):
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


class TestDrinkTracking(unittest.TestCase):
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
        with patch("builtins.input", return_value="Matti"):
            game._handlePostTask(makeTask("give", drinks=3), [drawer], drawer)
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
        with patch("builtins.input", return_value="Teppo:2 Matti:1"):
            game._handlePostTask(makeTask("social", drinks=3), list(game.players), game.players[0])
        self.assertEqual(game.players[0].getDrinksTaken(), 2)
        self.assertEqual(game.players[1].getDrinksTaken(), 1)

    def testSocialSkipOnEnter(self):
        game = TaskGame(players=makePlayers("Teppo", "Matti"))
        with patch("builtins.input", return_value=""):
            game._handlePostTask(makeTask("social", drinks=3), list(game.players), game.players[0])
        self.assertEqual(game.players[0].getDrinksTaken(), 0)
        self.assertEqual(game.players[1].getDrinksTaken(), 0)


class TestPlayerLinks(unittest.TestCase):
    def testPairStored(self):
        game = TaskGame(players=makePlayers("Teppo", "Matti"))
        drawer, partner = game.players[0], game.players[1]
        game._handlePostTask(makeTask("link", title="Pari", players=2), [partner], drawer)
        self.assertEqual(len(game.activePairs), 1)
        self.assertIn(drawer, game.activePairs[0])
        self.assertIn(partner, game.activePairs[0])

    def testPairReplacesPrevious(self):
        game = TaskGame(players=makePlayers("Teppo", "Matti", "Pekka"))
        p1, p2, p3 = game.players
        game.activePairs = [[p1, p2]]
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


class TestImmunity(unittest.TestCase):
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


class TestRoulette(unittest.TestCase):
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


class TestDeckCommand(unittest.TestCase):
    def testDeckCommandShowsCount(self):
        from printing.log import GameLog
        game = TaskGame(players=makePlayers("A"), log=GameLog(), config={"commonCount": 1, "specialCount": 1})
        with patch("games.taskGame.taskGame.TASKS", [makeTask("special", title="X", rarity="common")]):
            with patch("builtins.input", side_effect=["d", "", "", ""]):
                with patch("builtins.print") as mockPrint:
                    game.playRound()
        printed = [str(c) for c in mockPrint.call_args_list]
        self.assertTrue(any("Cards left" in c for c in printed))

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


class TestBuildPool(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
