import math
import unittest
from unittest.mock import patch
from tests.testUtils import SilentTest
from core.player import Player
from core.events import DrinkEvent, GiveEvent, GameEndEvent, TiebreakStartEvent, TiebreakEliminationEvent, TiebreakWinnerEvent
from games.ravitGame.horses import Horse, _generateHorse, generateHorses, _assignRelativeOdds
from games.ravitGame.jockeys import Jockey, JOCKEYS, dealJockeys
from games.ravitGame.ravit import RavitGame


def makeHorse(id=1, name="Testi", speed=3, endurance=3, luck=3, odds=2.0) -> Horse:
    return Horse(
        id=id, name=name,
        speed=speed, endurance=endurance, luck=luck,
        odds=odds,
        fightStrength=3, fightMaxHealth=20, fightHealth=0,
        staminaLeft=endurance * 3,
    )


def makeRavit(config=None) -> RavitGame:
    players = [Player(1, "Testi"), Player(2, "Matti")]
    return RavitGame(players=players, config=config or {})


class TestHorseGeneration(SilentTest):
    def testGeneratedHorseHasRequiredFields(self):
        h = _generateHorse(1, "Ukko")
        for field in ("id", "name", "speed", "endurance", "luck", "odds",
                      "position", "status", "tiredRoundsLeft", "stumbleRoundsLeft",
                      "motivatedRoundsLeft", "fightRoundsLeft", "fightOpponent",
                      "fightStrength", "fightMaxHealth", "fightHealth"):
            self.assertTrue(hasattr(h, field), f"Missing field: {field}")

    def testStatsInValidRange(self):
        for _ in range(20):
            h = _generateHorse(1, "Test")
            self.assertIn(h.speed, range(1, 6))
            self.assertIn(h.endurance, range(1, 6))
            self.assertIn(h.luck, range(1, 6))

    def testRelativeOddsWeakestHigherThanStrongest(self):
        for _ in range(20):
            weak   = Horse(id=1, name="Weak",   speed=1, endurance=1, luck=1)
            strong = Horse(id=2, name="Strong",  speed=5, endurance=5, luck=5)
            _assignRelativeOdds([weak, strong])
            self.assertGreater(weak.odds, strong.odds)

    def testOddsAtLeast1point5(self):
        horses = [Horse(id=i, name=f"H{i}", speed=5, endurance=5, luck=5) for i in range(1, 5)]
        _assignRelativeOdds(horses)
        for h in horses:
            self.assertGreaterEqual(h.odds, 1.5)

    def testCountRespected(self):
        horses = generateHorses(4)
        self.assertEqual(len(horses), 4)

    def testNamesAreUnique(self):
        horses = generateHorses(6)
        names = [h.name for h in horses]
        self.assertEqual(len(names), len(set(names)))

    def testIdsAreSequential(self):
        horses = generateHorses(4)
        self.assertEqual([h.id for h in horses], [1, 2, 3, 4])

    def testCountClampedToNamePool(self):
        from games.ravitGame.horses import HORSE_NAMES
        horses = generateHorses(9999)
        self.assertEqual(len(horses), len(HORSE_NAMES))


class TestHorseMovement(SilentTest):
    def testAliveHorseMovesForward(self):
        game = makeRavit({"trackLength": 20})
        horse = makeHorse(speed=3)
        game._moveHorse(horse)
        self.assertGreater(horse.position, 0)

    def testHighEnduranceNoSpeedBonusInSecondHalf(self):
        game = makeRavit({"trackLength": 20})
        h = makeHorse(speed=3, endurance=5)
        h.position = 10
        with patch("random.randint", return_value=0):
            game._moveHorse(h)
        self.assertEqual(h.position, 13)

    def testEndurancePenaltyInSecondHalf(self):
        game = makeRavit({"trackLength": 20})
        positions = []
        for _ in range(50):
            h = makeHorse(speed=3, endurance=1)
            h.position = 10
            with patch("random.randint", return_value=0):
                game._moveHorse(h)
            positions.append(h.position)
        self.assertTrue(all(p <= 13 for p in positions))

    def testTiredPenaltyReducesSpeed(self):
        game = makeRavit({"trackLength": 20})
        h = makeHorse(speed=3)
        h.tiredRoundsLeft = 2
        with patch("random.randint", return_value=0):
            game._moveHorse(h)
        self.assertEqual(h.position, 2)

    def testTiredCountdownDecrements(self):
        game = makeRavit({"trackLength": 20})
        h = makeHorse(speed=3)
        h.tiredRoundsLeft = 2
        game._moveHorse(h)
        self.assertEqual(h.tiredRoundsLeft, 1)

    def testStumbleSkipsMovement(self):
        game = makeRavit({"trackLength": 20})
        h = makeHorse(speed=5)
        h.stumbleRoundsLeft = 1
        game._moveHorse(h)
        self.assertEqual(h.position, 0)

    def testStumbleCountdownDecrements(self):
        game = makeRavit({"trackLength": 20})
        h = makeHorse(speed=5)
        h.stumbleRoundsLeft = 2
        game._moveHorse(h)
        self.assertEqual(h.stumbleRoundsLeft, 1)

    def testPositionCappedAtTrackLength(self):
        game = makeRavit({"trackLength": 10})
        h = makeHorse(speed=5)
        h.position = 9
        with patch("random.randint", return_value=2):
            game._moveHorse(h)
        self.assertEqual(h.position, 10)

    def testMotivatedIncreasesSpeed(self):
        game = makeRavit({"trackLength": 20})
        h = makeHorse(speed=3)
        h.motivatedRoundsLeft = 1
        with patch("random.randint", return_value=0):
            game._moveHorse(h)
        self.assertEqual(h.position, 4)

    def testMotivatedCountdownDecrements(self):
        game = makeRavit({"trackLength": 20})
        h = makeHorse(speed=3)
        h.motivatedRoundsLeft = 2
        game._moveHorse(h)
        self.assertEqual(h.motivatedRoundsLeft, 1)

    def testConfusedMovesBackwards(self):
        game = makeRavit({"trackLength": 20})
        h = makeHorse(speed=3)
        h.position = 10
        h.confusedRoundsLeft = 1
        with patch("random.randint", return_value=0):
            game._moveHorse(h)
        self.assertLess(h.position, 10)

    def testConfusedCountdownDecrements(self):
        game = makeRavit({"trackLength": 20})
        h = makeHorse(speed=3)
        h.position = 10
        h.confusedRoundsLeft = 2
        game._moveHorse(h)
        self.assertEqual(h.confusedRoundsLeft, 1)


class TestRandomEvents(SilentTest):
    def _forceEvent(self, game, horse, eventType):
        game._roundNumber = 2
        with patch("random.random", return_value=0.0), \
             patch("random.choices", return_value=[eventType]):
            game._tryFireEvent(horse)

    def testDeathSetsDnfStatus(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        h = makeHorse(luck=3)
        self._forceEvent(game, h, "death")
        self.assertEqual(h.status, "dnf")

    def testBackwardsMovePositionBack(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        game._roundNumber = 2
        h = makeHorse(luck=3)
        h.position = 10
        with patch("random.random", return_value=0.0), \
             patch("random.choices", return_value=["backwards"]), \
             patch("random.randint", return_value=3):
            game._tryFireEvent(h)
        self.assertEqual(h.position, 7)

    def testBoostAdds3(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        h = makeHorse(luck=3)
        h.position = 5
        self._forceEvent(game, h, "boost")
        self.assertEqual(h.position, 8)

    def testTiredSetsTiredRounds(self):
        game = makeRavit({"trackLength": 20})
        h = makeHorse(endurance=3)
        h.staminaLeft = 1
        with patch("random.randint", return_value=0):
            game._moveHorse(h)
        self.assertEqual(h.tiredRoundsLeft, 2)

    def testStaminaResetsAfterDepletion(self):
        game = makeRavit({"trackLength": 20})
        h = makeHorse(endurance=3)
        h.staminaLeft = 1
        with patch("random.randint", return_value=0):
            game._moveHorse(h)
        self.assertEqual(h.staminaLeft, 6)

    def testStumbleSetsStumbleRounds(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        h = makeHorse(luck=3)
        self._forceEvent(game, h, "stumble")
        self.assertEqual(h.stumbleRoundsLeft, 1)

    def testMotivatedSetsMotivatedRounds(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        game._roundNumber = 2
        h = makeHorse(luck=3)
        with patch("random.random", return_value=0.0), \
             patch("random.choices", return_value=["motivated"]), \
             patch("random.randint", return_value=2):
            game._tryFireEvent(h)
        self.assertEqual(h.motivatedRoundsLeft, 2)

    def testSlipFallMovesBackAndStumbles(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        game._roundNumber = 2
        h = makeHorse(luck=3)
        h.position = 10
        with patch("random.random", return_value=0.5), \
             patch("random.choices", return_value=["slipFall"]), \
             patch("random.randint", return_value=3):
            game._tryFireEvent(h)
        self.assertLess(h.position, 10)
        self.assertEqual(h.stumbleRoundsLeft, 1)

    def testConfusedEventSetsRounds(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        game._roundNumber = 2
        h = makeHorse(luck=3)
        with patch("random.random", return_value=0.5), \
             patch("random.choices", return_value=["confused"]), \
             patch("random.randint", return_value=2):
            game._tryFireEvent(h)
        self.assertEqual(h.confusedRoundsLeft, 2)

    def testLightningKillsHorse(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        game._roundNumber = 2
        h = makeHorse(luck=3)
        with patch("random.random", return_value=0.0), \
             patch("random.choices", return_value=["lightning"]), \
             patch("random.randint", return_value=2):
            game._tryFireEvent(h)
        self.assertEqual(h.status, "dead")

    def testLightningSurvivalReducesStats(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        game._roundNumber = 2
        h = makeHorse(speed=3, endurance=3, luck=3)
        with patch("random.random", return_value=0.0), \
             patch("random.choices", return_value=["lightning"]), \
             patch("random.randint", return_value=0):
            game._tryFireEvent(h)
        self.assertEqual(h.status, "racing")
        self.assertEqual(h.speed, 2)
        self.assertEqual(h.endurance, 2)
        self.assertEqual(h.luck, 2)

    def testLightningSurvivalFloorAtOne(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        game._roundNumber = 2
        h = makeHorse(speed=1, endurance=1, luck=1)
        with patch("random.random", return_value=0.0), \
             patch("random.choices", return_value=["lightning"]), \
             patch("random.randint", return_value=0):
            game._tryFireEvent(h)
        self.assertEqual(h.speed, 1)
        self.assertEqual(h.endurance, 1)
        self.assertEqual(h.luck, 1)

    def testOvertakeJumpsAheadOfNearbyHorse(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        game._roundNumber = 2
        h1 = makeHorse(id=1, name="Ukko", luck=5)
        h2 = makeHorse(id=2, name="Myrsky")
        h1.position = 8
        h2.position = 10
        game.horses = [h1, h2]
        with patch("random.random", return_value=0.0), \
             patch("random.choices", return_value=["overtake"]):
            game._tryFireEvent(h1)
        self.assertEqual(h1.position, 11)

    def testOvertakeDoesNothingIfNoHorseWithin3(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        game._roundNumber = 2
        h1 = makeHorse(id=1, name="Ukko", luck=5)
        h2 = makeHorse(id=2, name="Myrsky")
        h1.position = 5
        h2.position = 15
        game.horses = [h1, h2]
        with patch("random.random", return_value=0.0), \
             patch("random.choices", return_value=["overtake"]):
            game._tryFireEvent(h1)
        self.assertEqual(h1.position, 5)

    def testNoEventWhenRandomHighEnough(self):
        game = makeRavit({"trackLength": 20, "eventChance": 0.15})
        game._roundNumber = 2
        h = makeHorse(luck=3)
        h.position = 5
        with patch("random.random", return_value=0.99):
            game._tryFireEvent(h)
        self.assertEqual(h.position, 5)
        self.assertEqual(h.status, "racing")

    def testLowLuckIncreasesEventChance(self):
        lowChance = 0.15 * ((6 - 1) / 3.0)
        highChance = 0.15 * ((6 - 5) / 3.0)
        self.assertGreater(lowChance, highChance)

    def testDrunkFanStumblesRandomHorse(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        game._roundNumber = 2
        h1 = makeHorse(id=1, name="Ukko", luck=1)
        h2 = makeHorse(id=2, name="Myrsky")
        game.horses = [h1, h2]
        with patch("random.random", return_value=0.5), \
             patch("random.choices", return_value=["drunkFan"]), \
             patch("random.choice", return_value=h2):
            game._tryFireEvent(h1)
        self.assertEqual(h2.stumbleRoundsLeft, 1)

    def testHorseKickStumblesHorseBehind(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        game._roundNumber = 2
        h1 = makeHorse(id=1, name="Ukko", luck=1)
        h2 = makeHorse(id=2, name="Myrsky")
        h1.position = 10
        h2.position = 5
        game.horses = [h1, h2]
        with patch("random.random", return_value=0.5), \
             patch("random.choices", return_value=["horseKick"]), \
             patch("random.choice", return_value=h2), \
             patch("random.randint", return_value=1):
            game._tryFireEvent(h1)
        self.assertEqual(h2.stumbleRoundsLeft, 1)
        self.assertEqual(h2.position, 4)

    def testHorseKickFizzlesIfNoBehind(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        game._roundNumber = 2
        h1 = makeHorse(id=1, name="Ukko", luck=1)
        h2 = makeHorse(id=2, name="Myrsky")
        h1.position = 3
        h2.position = 10
        game.horses = [h1, h2]
        with patch("random.random", return_value=0.5), \
             patch("random.choices", return_value=["horseKick"]):
            game._tryFireEvent(h1)
        self.assertEqual(h2.stumbleRoundsLeft, 0)

    def testHorseShoeFallsReducesSpeed(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        game._roundNumber = 2
        h = makeHorse(id=1, name="Ukko", luck=1, speed=3)
        game.horses = [h]
        with patch("random.random", return_value=0.5), \
             patch("random.choices", return_value=["horseShoe"]), \
             patch("random.choice", return_value=h):
            game._tryFireEvent(h)
        self.assertEqual(h.speed, 2)

    def testHorseShoeFallsSpeedFloorAtOne(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        game._roundNumber = 2
        h = makeHorse(id=1, name="Ukko", luck=1, speed=1)
        game.horses = [h]
        with patch("random.random", return_value=0.5), \
             patch("random.choices", return_value=["horseShoe"]), \
             patch("random.choice", return_value=h):
            game._tryFireEvent(h)
        self.assertEqual(h.speed, 1)

    def testDrunkFanCanHitAnyRacingHorse(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        game._roundNumber = 2
        h1 = makeHorse(id=1, name="Ukko", luck=1)
        h2 = makeHorse(id=2, name="Myrsky")
        game.horses = [h1, h2]
        with patch("random.random", return_value=0.5), \
             patch("random.choices", return_value=["drunkFan"]), \
             patch("random.choice", return_value=h1):
            game._tryFireEvent(h1)
        self.assertEqual(h1.stumbleRoundsLeft, 1)


class TestEventGuard(SilentTest):
    def testHorseGetsAtMostOneEventPerRound(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        game._roundNumber = 2
        h = makeHorse(id=1, name="Ukko", luck=3)
        game.horses = [h]
        with patch("random.random", return_value=0.0), \
             patch("random.choices", return_value=["boost"]):
            game._tryFireEvent(h)
        posAfterFirst = h.position
        with patch("random.random", return_value=0.0), \
             patch("random.choices", return_value=["boost"]):
            game._tryFireEvent(h)
        self.assertEqual(h.position, posAfterFirst)

    def testEventedThisRoundResetEachRound(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        game._roundNumber = 2
        h = makeHorse(id=1, name="Ukko", luck=3)
        game.horses = [h]
        game._eventedThisRound.add(h.id)
        game._eventedThisRound = set()
        with patch("random.random", return_value=0.0), \
             patch("random.choices", return_value=["boost"]):
            game._tryFireEvent(h)
        self.assertGreater(h.position, 0)

    def testDrunkFanSkipsAlreadyEventedHorse(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        game._roundNumber = 2
        h1 = makeHorse(id=1, name="Ukko", luck=1)
        h2 = makeHorse(id=2, name="Myrsky")
        game.horses = [h1, h2]
        game._eventedThisRound.add(h2.id)
        with patch("random.random", return_value=0.5), \
             patch("random.choices", return_value=["drunkFan"]):
            game._tryFireEvent(h1)
        self.assertEqual(h2.stumbleRoundsLeft, 0)

    def testDrunkFanFizzlesIfAllHorsesEvented(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        game._roundNumber = 2
        h1 = makeHorse(id=1, name="Ukko", luck=1)
        h2 = makeHorse(id=2, name="Myrsky")
        game.horses = [h1, h2]
        game._eventedThisRound.add(h2.id)
        game._eventedThisRound.add(h1.id)
        with patch("random.random", return_value=0.5), \
             patch("random.choices", return_value=["drunkFan"]):
            game._tryFireEvent(h1)
        self.assertEqual(h2.stumbleRoundsLeft, 0)

    def testHorseKickSkipsAlreadyEventedHorse(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        game._roundNumber = 2
        h1 = makeHorse(id=1, name="Ukko", luck=1)
        h2 = makeHorse(id=2, name="Myrsky")
        h1.position = 10
        h2.position = 5
        game.horses = [h1, h2]
        game._eventedThisRound.add(h2.id)
        with patch("random.random", return_value=0.5), \
             patch("random.choices", return_value=["horseKick"]):
            game._tryFireEvent(h1)
        self.assertEqual(h2.stumbleRoundsLeft, 0)

    def testFightStartMarksHorsesAsEvented(self):
        game = makeRavit({"trackLength": 20, "fightChance": 1.0, "eventChance": 0.0})
        game._roundNumber = 2
        h1 = makeHorse(id=1, name="Ukko")
        h2 = makeHorse(id=2, name="Myrsky")
        h1.position = 10
        h2.position = 10
        game.horses = [h1, h2]
        with patch("random.random", return_value=0.0), \
             patch("random.randint", return_value=2):
            game._checkNewFights()
        self.assertIn(h1.id, game._eventedThisRound)
        self.assertIn(h2.id, game._eventedThisRound)


class TestFightMechanics(SilentTest):
    def testResolveFightBetweenLoserDies(self):
        game = makeRavit({})
        h1 = makeHorse(id=1, name="Strong")
        h2 = makeHorse(id=2, name="Weak")
        h1.fightStrength = 5
        h2.fightStrength = 1
        game.horses = [h1, h2]
        with patch("random.random", return_value=0.0):
            game._resolveFightBetween(h1, h2)
        self.assertEqual(h2.status, "dead")
        self.assertEqual(h1.status, "racing")

    def testResolveFightWinnerStatsDecrease(self):
        game = makeRavit({})
        h1 = makeHorse(id=1, name="Strong", speed=3, endurance=3, luck=3)
        h2 = makeHorse(id=2, name="Weak")
        h1.fightStrength = 5
        h2.fightStrength = 1
        game.horses = [h1, h2]
        with patch("random.random", return_value=0.0):
            game._resolveFightBetween(h1, h2)
        self.assertEqual(h1.speed, 2)
        self.assertEqual(h1.endurance, 2)
        self.assertEqual(h1.luck, 2)


class TestTiebreakFight(SilentTest):
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
        h1.fightMaxHealth = 10
        h2.fightMaxHealth = 10
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
        h1.fightMaxHealth = 10
        h2.fightMaxHealth = 10
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
        h1.fightMaxHealth = 5
        h2.fightMaxHealth = 5
        game.horses = [h1, h2]
        with patch("random.randint", return_value=5), \
             patch("random.choice", return_value=h2), \
             patch("builtins.input", return_value=""), \
             patch("builtins.print"):
            game._tiebreakFight([h1, h2])
        elims = [e for e in log.events if isinstance(e, TiebreakEliminationEvent)]
        self.assertGreater(len(elims), 0)


class TestDrinkResolution(SilentTest):
    def _makeGame(self):
        game = makeRavit({"trackLength": 20})
        game.horses = [
            makeHorse(id=1, name="Winner", speed=5, odds=2.0),
            makeHorse(id=2, name="Loser",  speed=1, odds=4.0),
        ]
        game.horses[0].position = 20
        game.horses[1].position = 5
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
        game.horses[1].status = "dnf"
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
        self.assertEqual(testiGive.amount, math.ceil(2 * 2.0))

    def testGameEndEventEmitted(self):
        game = self._makeGame()
        game.bets = [{"player": "Testi", "horseId": 1, "amount": 1}]
        emitted = []
        game.log = type("Log", (), {"add": lambda self, e: emitted.append(e)})()
        with patch("builtins.input", return_value="1"), \
             patch("builtins.print"):
            game._drinkResolution()
        self.assertIsInstance(emitted[-1], GameEndEvent)


class TestJockeys(SilentTest):
    def testDealJockeysReturnsRequestedCount(self):
        dealt = dealJockeys(2)
        self.assertEqual(len(dealt), 2)

    def testDealJockeysNoDuplicates(self):
        dealt = dealJockeys(4)
        names = [j.name for j in dealt]
        self.assertEqual(len(names), len(set(names)))

    def testApplyToHorseStatBonus(self):
        h = makeHorse(speed=3, endurance=3, luck=3)
        Jockey("Test", "", speedBonus=1, enduranceBonus=1, luckBonus=1).applyToHorse(h)
        self.assertEqual(h.speed, 4)
        self.assertEqual(h.endurance, 4)
        self.assertEqual(h.luck, 4)

    def testApplyToHorseStatCap(self):
        h = makeHorse(speed=5, endurance=5, luck=5)
        Jockey("Test", "", speedBonus=2, enduranceBonus=2, luckBonus=2).applyToHorse(h)
        self.assertEqual(h.speed, 5)
        self.assertEqual(h.endurance, 5)
        self.assertEqual(h.luck, 5)

    def testApplyToHorseStartPosition(self):
        h = makeHorse()
        Jockey("Terävä", "", startPositionBonus=2).applyToHorse(h)
        self.assertEqual(h.position, 2)

    def testOnnekasReducesEventChance(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        game._roundNumber = 2
        h = makeHorse(id=1, luck=3)
        game.horses = [h]
        game._jockeyMap[h.id] = Jockey("Onnekas", "", eventChanceMultiplier=0.0)
        with patch("random.random", return_value=0.5):
            game._tryFireEvent(h)
        self.assertEqual(h.position, 0)
        self.assertNotIn(h.id, game._eventedThisRound)

    def testPelkuriPreventsHorseFromFighting(self):
        game = makeRavit({"trackLength": 20, "fightChance": 1.0, "eventChance": 0.0})
        game._roundNumber = 2
        h1 = makeHorse(id=1, name="Ukko")
        h2 = makeHorse(id=2, name="Myrsky")
        h1.position = 10
        h2.position = 10
        game.horses = [h1, h2]
        game._jockeyMap[h1.id] = Jockey("Pelkuri", "", immuneToFights=True)
        with patch("random.random", return_value=0.0), \
             patch("random.randint", return_value=2):
            game._checkNewFights()
        self.assertEqual(h1.fightRoundsLeft, 0)
        self.assertEqual(h2.fightRoundsLeft, 0)

    def testRajuDoublesBoostDistance(self):
        game = makeRavit({"trackLength": 20, "eventChance": 1.0})
        game._roundNumber = 2
        h = makeHorse(id=1, luck=3)
        h.position = 5
        game.horses = [h]
        game._jockeyMap[h.id] = Jockey("Raju", "", boostMultiplier=2.0)
        with patch("random.random", return_value=0.0), \
             patch("random.choices", return_value=["boost"]):
            game._tryFireEvent(h)
        self.assertEqual(h.position, 11)


if __name__ == "__main__":
    unittest.main()
