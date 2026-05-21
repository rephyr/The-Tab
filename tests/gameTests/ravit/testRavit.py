import unittest
from unittest.mock import patch
from core.player import Player
from core.events import DrinkEvent, GiveEvent, GameEndEvent, TiebreakStartEvent, TiebreakEliminationEvent, TiebreakWinnerEvent
from games.ravitGame.horses import generateHorse, generateHorses, _assignRelativeOdds
from games.ravitGame.ravit import RavitGame


def makeHorse(id=1, name="Testi", speed=3, endurance=3, luck=3, odds=2.0) -> dict:
    return {
        "id": id, "name": name,
        "speed": speed, "endurance": endurance, "luck": luck,
        "odds": odds,
        "position": 0, "alive": True,
        "tiredRoundsLeft": 0, "stumbleRoundsLeft": 0,
        "motivatedRoundsLeft": 0,
        "fightRoundsLeft": 0, "fightOpponent": None,
        "fightStrength": 3, "fightMaxHealth": 20, "fightHealth": 0,
    }


def makeRavit(config=None) -> RavitGame:
    players = [Player(1, "Testi"), Player(2, "Matti")]
    return RavitGame(players=players, config=config or {})


class TestHorseGeneration(unittest.TestCase):
    def testGeneratedHorseHasRequiredKeys(self):
        h = generateHorse(1, "Ukko")
        for key in ("id", "name", "speed", "endurance", "luck", "odds",
                    "position", "alive", "tiredRoundsLeft", "stumbleRoundsLeft",
                    "motivatedRoundsLeft", "fightRoundsLeft", "fightOpponent",
                    "fightStrength", "fightMaxHealth", "fightHealth"):
            self.assertIn(key, h)

    def testStatsInValidRange(self):
        for _ in range(20):
            h = generateHorse(1, "Test")
            self.assertIn(h["speed"], range(1, 6))
            self.assertIn(h["endurance"], range(1, 6))
            self.assertIn(h["luck"], range(1, 6))

    def testRelativeOddsWeakestHigherThanStrongest(self):
        horses = [
            {"id": 1, "speed": 1, "endurance": 1, "luck": 1, "odds": 0.0},
            {"id": 2, "speed": 5, "endurance": 5, "luck": 5, "odds": 0.0},
        ]
        for _ in range(20):
            test = [dict(h) for h in horses]
            _assignRelativeOdds(test)
            self.assertGreater(test[0]["odds"], test[1]["odds"])

    def testOddsAtLeast1point5(self):
        horses = [
            {"id": i, "speed": 5, "endurance": 5, "luck": 5, "odds": 0.0}
            for i in range(1, 5)
        ]
        _assignRelativeOdds(horses)
        for h in horses:
            self.assertGreaterEqual(h["odds"], 1.5)

    def testCountRespected(self):
        horses = generateHorses(4)
        self.assertEqual(len(horses), 4)

    def testNamesAreUnique(self):
        horses = generateHorses(6)
        names = [h["name"] for h in horses]
        self.assertEqual(len(names), len(set(names)))

    def testIdsAreSequential(self):
        horses = generateHorses(4)
        self.assertEqual([h["id"] for h in horses], [1, 2, 3, 4])


class TestHorseMovement(unittest.TestCase):
    def testAliveHorseMovesForward(self):
        game = makeRavit({"trackLength": 20})
        horse = makeHorse(speed=3)
        game._moveHorse(horse)
        self.assertGreater(horse["position"], 0)

    def testEnduranceBonusInSecondHalf(self):
        game = makeRavit({"trackLength": 20})
        positions = []
        for _ in range(50):
            h = makeHorse(speed=3, endurance=5)
            h["position"] = 10
            with patch("random.randint", return_value=0):
                game._moveHorse(h)
            positions.append(h["position"])
        self.assertTrue(all(p >= 14 for p in positions))

    def testEndurancePenaltyInSecondHalf(self):
        game = makeRavit({"trackLength": 20})
        positions = []
        for _ in range(50):
            h = makeHorse(speed=3, endurance=1)
            h["position"] = 10
            with patch("random.randint", return_value=0):
                game._moveHorse(h)
            positions.append(h["position"])
        self.assertTrue(all(p <= 13 for p in positions))

    def testTiredPenaltyReducesSpeed(self):
        game = makeRavit({"trackLength": 20})
        h = makeHorse(speed=3)
        h["tiredRoundsLeft"] = 2
        with patch("random.randint", return_value=0):
            game._moveHorse(h)
        self.assertEqual(h["position"], 2)

    def testTiredCountdownDecrements(self):
        game = makeRavit({"trackLength": 20})
        h = makeHorse(speed=3)
        h["tiredRoundsLeft"] = 2
        game._moveHorse(h)
        self.assertEqual(h["tiredRoundsLeft"], 1)

    def testStumbleSkipsMovement(self):
        game = makeRavit({"trackLength": 20})
        h = makeHorse(speed=5)
        h["stumbleRoundsLeft"] = 1
        game._moveHorse(h)
        self.assertEqual(h["position"], 0)

    def testStumbleCountdownDecrements(self):
        game = makeRavit({"trackLength": 20})
        h = makeHorse(speed=5)
        h["stumbleRoundsLeft"] = 2
        game._moveHorse(h)
        self.assertEqual(h["stumbleRoundsLeft"], 1)

    def testPositionCappedAtTrackLength(self):
        game = makeRavit({"trackLength": 10})
        h = makeHorse(speed=5)
        h["position"] = 9
        with patch("random.randint", return_value=2):
            game._moveHorse(h)
        self.assertEqual(h["position"], 10)

    def testMotivatedIncreasesSpeed(self):
        game = makeRavit({"trackLength": 20})
        h = makeHorse(speed=3)
        h["motivatedRoundsLeft"] = 1
        with patch("random.randint", return_value=0):
            game._moveHorse(h)
        self.assertEqual(h["position"], 4)

    def testMotivatedCountdownDecrements(self):
        game = makeRavit({"trackLength": 20})
        h = makeHorse(speed=3)
        h["motivatedRoundsLeft"] = 2
        game._moveHorse(h)
        self.assertEqual(h["motivatedRoundsLeft"], 1)


class TestRandomEvents(unittest.TestCase):
    def _forceEvent(self, game, horse, eventType):
        with patch("random.random", return_value=0.0), \
             patch("random.choices", return_value=[eventType]):
            game._tryFireEvent(horse)

    def testDeathSetsAliveToFalse(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        h = makeHorse(luck=3)
        self._forceEvent(game, h, "death")
        self.assertFalse(h["alive"])

    def testBackwardsMovePositionBack(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        h = makeHorse(luck=3)
        h["position"] = 10
        with patch("random.random", return_value=0.0), \
             patch("random.choices", return_value=["backwards"]), \
             patch("random.randint", return_value=3):
            game._tryFireEvent(h)
        self.assertEqual(h["position"], 7)

    def testBoostAdds3(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        h = makeHorse(luck=3)
        h["position"] = 5
        self._forceEvent(game, h, "boost")
        self.assertEqual(h["position"], 8)

    def testTiredSetsTiredRounds(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        h = makeHorse(luck=3)
        self._forceEvent(game, h, "tired")
        self.assertEqual(h["tiredRoundsLeft"], 2)

    def testStumbleSetsStumbleRounds(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        h = makeHorse(luck=3)
        self._forceEvent(game, h, "stumble")
        self.assertEqual(h["stumbleRoundsLeft"], 1)

    def testMotivatedSetsMotivatedRounds(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        h = makeHorse(luck=3)
        with patch("random.random", return_value=0.0), \
             patch("random.choices", return_value=["motivated"]), \
             patch("random.randint", return_value=2):
            game._tryFireEvent(h)
        self.assertEqual(h["motivatedRoundsLeft"], 2)

    def testNoEventWhenRandomHighEnough(self):
        game = makeRavit({"trackLength": 20, "eventChance": 0.15})
        h = makeHorse(luck=3)
        h["position"] = 5
        with patch("random.random", return_value=0.99):
            game._tryFireEvent(h)
        self.assertEqual(h["position"], 5)
        self.assertTrue(h["alive"])

    def testLowLuckIncreasesEventChance(self):
        lowChance = 0.15 * ((6 - 1) / 3.0)
        highChance = 0.15 * ((6 - 5) / 3.0)
        self.assertGreater(lowChance, highChance)


class TestFightMechanics(unittest.TestCase):
    def testResolveFightBetweenLoserDies(self):
        game = makeRavit({})
        h1 = makeHorse(id=1, name="Strong")
        h2 = makeHorse(id=2, name="Weak")
        h1["fightStrength"] = 5
        h2["fightStrength"] = 1
        game.horses = [h1, h2]
        with patch("random.random", return_value=0.0):
            game._resolveFightBetween(h1, h2)
        self.assertFalse(h2["alive"])
        self.assertTrue(h1["alive"])

    def testResolveFightWinnerStatsDecrease(self):
        game = makeRavit({})
        h1 = makeHorse(id=1, name="Strong", speed=3, endurance=3, luck=3)
        h2 = makeHorse(id=2, name="Weak")
        h1["fightStrength"] = 5
        h2["fightStrength"] = 1
        game.horses = [h1, h2]
        with patch("random.random", return_value=0.0):
            game._resolveFightBetween(h1, h2)
        self.assertEqual(h1["speed"], 2)
        self.assertEqual(h1["endurance"], 2)
        self.assertEqual(h1["luck"], 2)


class TestTiebreakFight(unittest.TestCase):
    def _makeGameWithLog(self):
        players = [Player(1, "Testi"), Player(2, "Matti")]
        from printing.log import GameLog
        log = GameLog()
        game = RavitGame(players=players, config={"trackLength": 20}, log=log)
        return game, log

    def testTiebreakStartEventEmitted(self):
        game, log = self._makeGameWithLog()
        h1 = makeHorse(id=1, name="Ukko")
        h2 = makeHorse(id=2, name="Myrsky")
        h1["fightMaxHealth"] = 10
        h2["fightMaxHealth"] = 10
        game.horses = [h1, h2]
        with patch("random.randint", return_value=5), \
             patch("random.choice", return_value=h2), \
             patch("builtins.input", return_value=""), \
             patch("builtins.print"):
            game._tiebreakFight([h1, h2])
        starts = [e for e in log.events if isinstance(e, TiebreakStartEvent)]
        self.assertEqual(len(starts), 1)
        self.assertEqual(len(starts[0].combatants), 2)

    def testTiebreakWinnerEventEmitted(self):
        game, log = self._makeGameWithLog()
        h1 = makeHorse(id=1, name="Ukko")
        h2 = makeHorse(id=2, name="Myrsky")
        h1["fightMaxHealth"] = 10
        h2["fightMaxHealth"] = 10
        game.horses = [h1, h2]
        with patch("random.randint", return_value=5), \
             patch("random.choice", return_value=h2), \
             patch("builtins.input", return_value=""), \
             patch("builtins.print"):
            game._tiebreakFight([h1, h2])
        winners = [e for e in log.events if isinstance(e, TiebreakWinnerEvent)]
        self.assertEqual(len(winners), 1)

    def testTiebreakEliminationEventEmitted(self):
        game, log = self._makeGameWithLog()
        h1 = makeHorse(id=1, name="Ukko")
        h2 = makeHorse(id=2, name="Myrsky")
        h1["fightMaxHealth"] = 5
        h2["fightMaxHealth"] = 5
        game.horses = [h1, h2]
        with patch("random.randint", return_value=5), \
             patch("random.choice", return_value=h2), \
             patch("builtins.input", return_value=""), \
             patch("builtins.print"):
            game._tiebreakFight([h1, h2])
        elims = [e for e in log.events if isinstance(e, TiebreakEliminationEvent)]
        self.assertGreater(len(elims), 0)


class TestDrinkResolution(unittest.TestCase):
    def _makeGame(self):
        game = makeRavit({"trackLength": 20})
        game.horses = [
            makeHorse(id=1, name="Winner", speed=5, odds=2.0),
            makeHorse(id=2, name="Loser",  speed=1, odds=4.0),
        ]
        game.horses[0]["position"] = 20
        game.horses[1]["position"] = 5
        return game

    def testWinnerBettorGivesToLastPlace(self):
        game = self._makeGame()
        game.bets = [
            {"player": "Testi", "horseId": 1, "amount": 2},
            {"player": "Matti", "horseId": 2, "amount": 3},
        ]
        emitted = []
        game.log = type("Log", (), {"add": lambda self, e: emitted.append(e)})()
        with patch("builtins.input", return_value="1"), \
             patch("builtins.print"):
            game._drinkResolution()
        giveEvents = [e for e in emitted if isinstance(e, GiveEvent)]
        self.assertTrue(any(e.giver == "Testi" for e in giveEvents))

    def testLoserBettorDrinks(self):
        game = self._makeGame()
        game.bets = [
            {"player": "Testi", "horseId": 1, "amount": 2},
            {"player": "Matti", "horseId": 2, "amount": 3},
        ]
        emitted = []
        game.log = type("Log", (), {"add": lambda self, e: emitted.append(e)})()
        with patch("builtins.input", return_value="1"), \
             patch("builtins.print"):
            game._drinkResolution()
        drinkEvents = [e for e in emitted if isinstance(e, DrinkEvent)]
        mattiDrink = next((e for e in drinkEvents if e.player == "Matti"), None)
        self.assertIsNotNone(mattiDrink)
        self.assertEqual(mattiDrink.amount, 3)

    def testDeadHorseBettorDrinksDouble(self):
        game = self._makeGame()
        game.horses[1]["alive"] = False
        game.bets = [
            {"player": "Testi", "horseId": 1, "amount": 2},
            {"player": "Matti", "horseId": 2, "amount": 3},
        ]
        emitted = []
        game.log = type("Log", (), {"add": lambda self, e: emitted.append(e)})()
        with patch("builtins.input", return_value="1"), \
             patch("builtins.print"):
            game._drinkResolution()
        drinkEvents = [e for e in emitted if isinstance(e, DrinkEvent)]
        mattiDrink = next((e for e in drinkEvents if e.player == "Matti"), None)
        self.assertIsNotNone(mattiDrink)
        self.assertEqual(mattiDrink.amount, 6)

    def testWinnerGiveAmountMultipliedByOdds(self):
        import math
        game = self._makeGame()
        game.bets = [
            {"player": "Testi", "horseId": 1, "amount": 2},
            {"player": "Matti", "horseId": 2, "amount": 3},
        ]
        emitted = []
        game.log = type("Log", (), {"add": lambda self, e: emitted.append(e)})()
        with patch("builtins.input", return_value="1"), \
             patch("builtins.print"):
            game._drinkResolution()
        giveEvents = [e for e in emitted if isinstance(e, GiveEvent)]
        testiGive = next((e for e in giveEvents if e.giver == "Testi"), None)
        self.assertIsNotNone(testiGive)
        expected = math.ceil(2 * 2.0)
        self.assertEqual(testiGive.amount, expected)

    def testGameEndEventEmitted(self):
        game = self._makeGame()
        game.bets = [{"player": "Testi", "horseId": 1, "amount": 1}]
        emitted = []
        game.log = type("Log", (), {"add": lambda self, e: emitted.append(e)})()
        with patch("builtins.input", return_value="1"), \
             patch("builtins.print"):
            game._drinkResolution()
        self.assertIsInstance(emitted[-1], GameEndEvent)


if __name__ == "__main__":
    unittest.main()
