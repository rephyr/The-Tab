"""
RavitGame — Finnish trotting-race drinking game.

Before the race each player bets a number of drinks on a horse.
The race runs in rounds with random events (boosts, falls, fights, lightning).
After the race: bettors on dead/DNF horses drink double their bet; bettors on the
winner give drinks (bet × odds, rounded up) to last-place bettors; all others
drink their bet amount.
"""
import random
import math
from dataclasses import dataclass, field
from core.game import Game
from core.events import (
    GameStartEvent, GameEndEvent,
    DrinkEvent,
    RaceStartEvent, BetsPlacedEvent, RaceRoundEvent, HorseEventFiredEvent, RaceFinishedEvent,
    TiebreakStartEvent, TiebreakRoundEvent, TiebreakEliminationEvent, TiebreakWinnerEvent,
)
from games.ravitGame.horses import generateHorses


@dataclass
class RavitGame(Game):
    """Drinking-game horse race. Call playRound() to run one full game."""

    gameTitle: str = "Ravit"
    config: dict = field(default_factory=dict)
    horses: list = field(default_factory=list)
    bets: list = field(default_factory=list)
    _roundNumber: int = field(default=0, init=False, repr=False)
    _roundEvents: list = field(default_factory=list, init=False, repr=False)

    def playRound(self) -> None:
        self.emit(GameStartEvent([p.getName() for p in self.players]))
        self._setupHorses()
        self._bettingPhase()
        self._raceLoop()
        self._resolveFinish()
        self._drinkResolution()

    def _setupHorses(self) -> None:
        count = self._getConfig("horseCount", 4)
        self.horses = generateHorses(count)

    def _bettingPhase(self) -> None:
        print("\n=== VEDONLYÖNTI ===\n")
        debug = self._getConfig("debug", False)
        for h in self.horses:
            stats = f"  [nop:{h['speed']} kes:{h['endurance']} tur:{h['luck']} voi:{h['fightStrength']} hp:{h['fightMaxHealth']}]" if debug else ""
            print(f"{h['id']}. {h['name']:<{self._nameWidth()}}  kerroin: x{h['odds']}{stats}")
        print()

        self.emit(RaceStartEvent(
            players=[p.getName() for p in self.players],
            horses=[dict(h) for h in self.horses],
        ))

        maxBet = self._getConfig("maxBet", 5)
        for player in self.players:
            print(f"{player.getName()}n panos:")
            while True:
                raw = input(f"  Hevonen (1–{len(self.horses)}): ").strip()
                if raw.isdigit() and 1 <= int(raw) <= len(self.horses):
                    horseId = int(raw)
                    break
                print("  Virheellinen valinta.")
            while True:
                raw = input(f"  Panos (1–{maxBet}): ").strip()
                if raw.isdigit() and 1 <= int(raw) <= maxBet:
                    amount = int(raw)
                    break
                print("  Virheellinen arvo.")
            self.bets.append({"player": player.getName(), "horseId": horseId, "amount": amount})
            print()

        self.emit(BetsPlacedEvent(
            horses=[dict(h) for h in self.horses],
            bets=list(self.bets),
        ))

    def _raceLoop(self) -> None:
        trackLength = self._getConfig("trackLength", 20)
        print("\n=== STARTTIVIIVA ===")
        for horse in self.horses:
            bar = "@" + "-" * 22
            print(f"{horse['name']:<{self._nameWidth()}} [{bar}]  0/{trackLength}")
        startPositions = [
            {"id": h["id"], "name": h["name"], "position": 0, "status": "racing",
             "tiredRoundsLeft": 0, "stumbleRoundsLeft": 0, "motivatedRoundsLeft": 0,
             "fightRoundsLeft": 0, "confusedRoundsLeft": 0}
            for h in self.horses
        ]
        self.emit(RaceRoundEvent(roundNumber=0, trackLength=trackLength, positions=startPositions, raceEvents=[]))
        input("\nKilpailu alkaa! Paina Enter edetäksesi.\n")
        while True:
            self._roundNumber += 1
            self._runOneRound()
            aliveHorses = [h for h in self.horses if h["status"] == "racing"]
            if not aliveHorses or any(h["position"] >= trackLength for h in aliveHorses):
                break
            input("\nPaina Enter jatkaaksesi...")

    def _runOneRound(self) -> None:
        self._roundEvents = []
        self._resolveFights()
        self._checkNewFights()
        for horse in self.horses:
            if horse["status"] != "racing" or horse["fightRoundsLeft"] > 0:
                continue
            self._tryFireEvent(horse)
            if horse["status"] == "racing":
                self._moveHorse(horse)
        trackLength = self._getConfig("trackLength", 20)
        positions = [
            {
                "id": h["id"], "name": h["name"], "position": h["position"],
                "status": h["status"],
                "tiredRoundsLeft": h["tiredRoundsLeft"],
                "stumbleRoundsLeft": h["stumbleRoundsLeft"],
                "motivatedRoundsLeft": h["motivatedRoundsLeft"],
                "fightRoundsLeft": h["fightRoundsLeft"],
                "confusedRoundsLeft": h["confusedRoundsLeft"],
            }
            for h in self.horses
        ]
        self.emit(RaceRoundEvent(
            roundNumber=self._roundNumber,
            trackLength=trackLength,
            positions=positions,
            raceEvents=list(self._roundEvents),
        ))
        self._printTrack()

    def _checkNewFights(self) -> None:
        fightChance = self._getConfig("fightChance", 0.35)
        free = [h for h in self.horses if h["status"] == "racing" and h["fightRoundsLeft"] == 0 and h["position"] > 5]
        fighting = set()
        for i, h1 in enumerate(free):
            if h1["id"] in fighting:
                continue
            for h2 in free[i + 1:]:
                if h2["id"] in fighting:
                    continue
                if abs(h1["position"] - h2["position"]) <= 1 and random.random() < fightChance:
                    rounds = random.randint(1, 3)
                    h1["fightRoundsLeft"] = rounds
                    h1["fightOpponent"] = h2["id"]
                    h2["fightRoundsLeft"] = rounds
                    h2["fightOpponent"] = h1["id"]
                    fighting.add(h1["id"])
                    fighting.add(h2["id"])
                    detail = f"{h1['name']} ja {h2['name']} tappelevat!"
                    print(f"  *** {detail}")
                    self._roundEvents.append({"horseName": h1["name"], "eventType": "fight_start", "detail": detail})
                    self.emit(HorseEventFiredEvent(
                        roundNumber=self._roundNumber,
                        horseId=h1["id"],
                        horseName=h1["name"],
                        eventType="fight_start",
                        detail=detail,
                    ))
                    break

    def _resolveFights(self) -> None:
        processed = set()
        for horse in self.horses:
            if horse["status"] != "racing" or horse["fightRoundsLeft"] <= 0 or horse["id"] in processed:
                continue
            opponent = self._getHorseById(horse["fightOpponent"])
            processed.add(horse["id"])
            processed.add(opponent["id"])
            horse["fightRoundsLeft"] -= 1
            opponent["fightRoundsLeft"] -= 1
            if horse["fightRoundsLeft"] <= 0:
                if opponent["status"] != "racing":
                    horse["fightOpponent"] = None
                else:
                    self._resolveFightBetween(horse, opponent)

    def _resolveFightBetween(self, h1: dict, h2: dict) -> None:
        """Determine fight winner by strength ratio; loser dies, winner loses 1 in all stats."""
        total = h1["fightStrength"] + h2["fightStrength"]
        winner, loser = (h1, h2) if random.random() < h1["fightStrength"] / total else (h2, h1)
        loser["status"] = "dead"
        winner["fightRoundsLeft"] = 0
        winner["fightOpponent"] = None
        for stat in ("speed", "endurance", "luck"):
            winner[stat] = max(1, winner[stat] - 1)
        detail = (
            f"Tappelu ohi! {winner['name']} voitti — {loser['name']} kuoli! "
            f"{winner['name']} on loukkaantunut (kaikki tilastot -1)!"
        )
        print(f"  *** {detail}")
        self._roundEvents.append({"horseName": winner["name"], "eventType": "fight_win", "detail": detail})
        self.emit(HorseEventFiredEvent(
            roundNumber=self._roundNumber,
            horseId=loser["id"],
            horseName=loser["name"],
            eventType="fightDeath",
            detail=detail,
        ))

    def _tiebreakFight(self, tied: list) -> dict:
        """Run interactive multi-round combat between tied finishers; returns the surviving winner."""
        print("\n" + "=" * 40)
        print("  *** TASAPELI! VALMISTAUTUKAA LOPPUKAMPPAILUUN! ***")
        print("=" * 40)
        names = ", ".join(h["name"] for h in tied)
        print(f"\n{names} ylittävät maaliviivan samaan aikaan!")
        self.emit(TiebreakStartEvent(
            combatants=[{
                "id": h["id"], "name": h["name"], "odds": h["odds"],
                "health": h["fightMaxHealth"], "maxHealth": h["fightMaxHealth"],
                "strength": h["fightStrength"],
            } for h in tied]
        ))

        combatants = list(tied)
        for h in combatants:
            h["fightHealth"] = h["fightMaxHealth"]

        self._printCombatantBars(combatants)
        input("\nPaina Enter aloittaaksesi taistelun...")

        roundNum = 0
        while len(combatants) > 1:
            roundNum += 1
            print(f"\n  --- TAISTELUKIERROS {roundNum} ---")
            input("  Paina Enter...")

            thisRound = list(combatants)
            for attacker in thisRound:
                targets = [h for h in thisRound if h["id"] != attacker["id"]]
                target = random.choice(targets)
                damage = random.randint(1, attacker["fightStrength"])
                target["fightHealth"] = max(0, target["fightHealth"] - damage)
                print(f"  {attacker['name']:<12} -> {target['name']}: -{damage} HP")

            eliminated = [h for h in thisRound if h["fightHealth"] <= 0]
            combatants = [h for h in thisRound if h["fightHealth"] > 0]

            if not combatants:
                survivor = random.choice(eliminated)
                survivor["fightHealth"] = 1
                combatants = [survivor]
                eliminated = [h for h in eliminated if h["id"] != survivor["id"]]

            self._printCombatantBars(thisRound)

            allState = [
                {"name": h["name"], "health": h["fightHealth"],
                 "maxHealth": h["fightMaxHealth"], "strength": h["fightStrength"]}
                for h in thisRound
            ]
            self.emit(TiebreakRoundEvent(roundNumber=roundNum, combatants=allState))

            for loser in eliminated:
                print(f"\n  *** {loser['name']} kuoli!")
                self.emit(TiebreakEliminationEvent(
                    loserName=loser["name"],
                    remaining=[h["name"] for h in combatants],
                    combatants=allState,
                ))

        winner = combatants[0]
        print(f"\n{'*' * 40}")
        print(f"  {winner['name'].upper()} VOITTAA LOPPUKAMPPAILUN!")
        print(f"{'*' * 40}\n")
        self.emit(TiebreakWinnerEvent(
            winnerName=winner["name"],
            health=winner["fightHealth"],
            maxHealth=winner["fightMaxHealth"],
            strength=winner["fightStrength"],
        ))
        return winner

    def _printCombatantBars(self, combatants: list) -> None:
        print()
        for h in combatants:
            hp = h["fightHealth"]
            maxHp = h["fightMaxHealth"]
            filled = int(hp / maxHp * 16) if maxHp > 0 else 0
            bar = "█" * filled + "░" * (16 - filled)
            status = " [KUOLI]" if hp <= 0 else f"  (v:{h['fightStrength']})"
            print(f"  {h['name']:<12} [{bar}] {hp:>3}/{maxHp}{status}")

    def _resolveFinish(self) -> None:
        """Rank horses, trigger tiebreak if the top positions are within 1 tile, emit RaceFinishedEvent."""
        trackLength = self._getConfig("trackLength", 20)
        aliveHorses = [h for h in self.horses if h["status"] == "racing"]
        outHorses = [h for h in self.horses if h["status"] != "racing"]

        aliveHorses.sort(key=lambda h: h["position"], reverse=True)

        if aliveHorses:
            topPos = aliveHorses[0]["position"]
            closeFinish = [h for h in aliveHorses if topPos - h["position"] <= 1]
            if len(closeFinish) > 1:
                winner = self._tiebreakFight(closeFinish)
                aliveHorses = [winner] + [h for h in aliveHorses if h["id"] != winner["id"]]

        finalPositions = []
        for place, horse in enumerate(aliveHorses, start=1):
            displayPos = horse["position"] if place == 1 else min(horse["position"], trackLength - 1)
            finalPositions.append({
                "horseId": horse["id"],
                "horseName": horse["name"],
                "position": displayPos,
                "place": place,
                "status": "racing",
            })

        nextPlace = len(aliveHorses) + 1
        dnfHorses = sorted([h for h in outHorses if h["status"] == "dnf"], key=lambda h: -h["position"])
        deadHorses = sorted([h for h in outHorses if h["status"] == "dead"], key=lambda h: -h["position"])
        for horse in dnfHorses + deadHorses:
            finalPositions.append({
                "horseId": horse["id"],
                "horseName": horse["name"],
                "position": horse["position"],
                "place": nextPlace,
                "status": horse["status"],
            })
            nextPlace += 1

        print("\n=== LOPPUTULOS ===")
        for fp in finalPositions:
            if fp["status"] == "racing":
                print(f"{fp['place']}. {fp['horseName']:<{self._nameWidth()}} {fp['position']}/{trackLength} ruutua")
            else:
                label = "[KUOLI]" if fp["status"] == "dead" else "[DNF]"
                print(f"   {label} {fp['horseName']}")

        self.emit(RaceFinishedEvent(
            roundNumber=self._roundNumber,
            finalPositions=finalPositions,
        ))

    def _drinkResolution(self) -> None:
        """Assign drinks: dead-horse bettors drink double, winner gives to last-place bettors, rest drink their bet."""
        aliveHorses = [h for h in self.horses if h["status"] == "racing"]
        if not aliveHorses:
            # Edge case: all dead no winner
            for bet in self.bets:
                player = self._findPlayer(bet["player"])
                if player:
                    player.addDrinks(bet["amount"] * 2)
                    self.emit(DrinkEvent(player=bet["player"], amount=bet["amount"] * 2, reason="hevonen kuoli"))
        else:
            winnerId = max(aliveHorses, key=lambda h: h["position"])["id"]
            minPos = min(h["position"] for h in aliveHorses)
            lastPlaceIds = {h["id"] for h in aliveHorses if h["position"] == minPos}

            for bet in self.bets:
                player = self._findPlayer(bet["player"])
                if not player:
                    continue
                horse = self._getHorseById(bet["horseId"])
                if horse["status"] != "racing":
                    reason = "hevonen kuoli" if horse["status"] == "dead" else "hevonen ei pystynyt jatkamaan"
                    player.addDrinks(bet["amount"] * 2)
                    self.emit(DrinkEvent(player=bet["player"], amount=bet["amount"] * 2, reason=reason))
                elif horse["id"] == winnerId:
                    if lastPlaceIds:
                        player.pendingGive += math.ceil(bet["amount"] * horse["odds"])
                else:
                    player.addDrinks(bet["amount"])
                    self.emit(DrinkEvent(player=bet["player"], amount=bet["amount"], reason="hevonen hävisi"))

        self._interactiveGivePhase()

        scores = [
            {"name": p.getName(), "drinksTaken": p.getDrinksTaken(), "drinksToGive": p.drinksToGive}
            for p in self.players
        ]
        self.emit(GameEndEvent(scores=scores))

        print("\n=== JUOMAT ===")
        for s in scores:
            print(f"{s['name']}: joi {s['drinksTaken']} | antoi {s['drinksToGive']}")

    def _moveHorse(self, horse: dict) -> None:
        """Advance horse one round, applying stamina depletion, tired/stumble/confused/motivated effects."""
        trackLength = self._getConfig("trackLength", 20)
        if horse["stumbleRoundsLeft"] > 0:
            horse["stumbleRoundsLeft"] -= 1
            if horse["motivatedRoundsLeft"] > 0:
                horse["motivatedRoundsLeft"] -= 1
            if horse["tiredRoundsLeft"] > 0:
                horse["tiredRoundsLeft"] -= 1
            if horse["confusedRoundsLeft"] > 0:
                horse["confusedRoundsLeft"] -= 1
            return

        baseRoll = random.randint(0, 2)
        effectiveSpeed = horse["speed"]
        wasTired = horse["tiredRoundsLeft"] > 0
        if wasTired:
            effectiveSpeed = max(1, effectiveSpeed - 1)
            horse["tiredRoundsLeft"] -= 1
        if horse["motivatedRoundsLeft"] > 0:
            effectiveSpeed += 1
            horse["motivatedRoundsLeft"] -= 1

        if horse["confusedRoundsLeft"] > 0:
            horse["confusedRoundsLeft"] -= 1
            horse["position"] = max(0, horse["position"] - (effectiveSpeed + baseRoll))
            return

        move = effectiveSpeed + baseRoll
        halfway = trackLength // 2
        if horse["position"] >= halfway:
            if horse["endurance"] <= 2:
                move = max(1, move - 1)

        horse["position"] = min(horse["position"] + move, trackLength)

        if not wasTired:
            horse["staminaLeft"] -= 1
            if horse["staminaLeft"] <= 0:
                horse["tiredRoundsLeft"] = 2
                horse["staminaLeft"] = max(1, horse["endurance"] * 2)

    def _tryFireEvent(self, horse: dict) -> None:
        """Roll for a random event; positive events scale with luck, negative events scale inversely."""
        if self._roundNumber <= 1:
            return
        baseChance = self._getConfig("eventChance", 0.15)
        posChance = min(baseChance * (horse["luck"] / 3.0), 0.95)
        negChance = min(baseChance * ((6 - horse["luck"]) / 3.0), 0.95)

        r = random.random()
        if r < posChance:
            eventType = random.choices(
                ["boost", "motivated", "overtake"],
                weights=[4, 4, 3],
            )[0]
        elif r < posChance + negChance:
            eventType = random.choices(
                ["death", "backwards", "stumble", "slipFall", "confused", "lightning"],
                weights=[1, 3, 3, 3, 2, 2],
            )[0]
        else:
            return

        trackLength = self._getConfig("trackLength", 20)

        if eventType == "overtake":
            aheadHorses = [
                h for h in self.horses
                if h["status"] == "racing" and h["id"] != horse["id"]
                and 0 < h["position"] - horse["position"] <= 3
            ]
            if not aheadHorses:
                return
            target = min(aheadHorses, key=lambda h: h["position"])
            horse["position"] = min(target["position"] + 1, trackLength)
            detail = f"{horse['name']} juoksee hevosen {target['name']} imussa ja ohittaa hänet!"
        elif eventType == "boost":
            horse["position"] = min(horse["position"] + 3, trackLength)
            detail = f"{horse['name']} tekee tempun ja loikkaa 3 ruutua eteenpäin!"
        elif eventType == "motivated":
            rounds = random.randint(1, 3)
            horse["motivatedRoundsLeft"] = rounds
            detail = f"{horse['name']} on inspiroitunut. Hän juoksee vauhdikkaasti vielä {rounds} kierrosta!"
        elif eventType == "death":
            horse["status"] = "dnf"
            detail = f"{horse['name']} ei pysty jatkamaan ja poistuu kilpailusta!"
        elif eventType == "backwards":
            tiles = random.randint(2, 3)
            horse["position"] = max(0, horse["position"] - tiles)
            detail = f"{horse['name']} kompastuu ja peruuttaa {tiles} ruutua!"
        elif eventType == "stumble":
            horse["stumbleRoundsLeft"] = 1
            detail = f"{horse['name']} kompuroi. {horse['name']} ottaa lepiä maassa!"
        elif eventType == "slipFall":
            tiles = random.randint(2, 3)
            horse["position"] = max(0, horse["position"] - tiles)
            horse["stumbleRoundsLeft"] = 1
            detail = f"{horse['name']} liukastuu ja menee {tiles} ruutua taaksepäin!"
        elif eventType == "confused":
            rounds = random.randint(1, 2)
            horse["confusedRoundsLeft"] = rounds
            detail = f"{horse['name']} eksyy ja juoksee väärään suuntaan vielä {rounds} kierrosta!"
        elif eventType == "lightning":
            horse["status"] = "dead"
            detail = f"Salama iskee! {horse['name']} kuolee saman tien :(!"
        else:
            return

        print(f"  *** {detail}")
        self._roundEvents.append({"horseName": horse["name"], "eventType": eventType, "detail": detail})
        self.emit(HorseEventFiredEvent(
            roundNumber=self._roundNumber,
            horseId=horse["id"],
            horseName=horse["name"],
            eventType=eventType,
            detail=detail,
        ))

    def _printTrack(self) -> None:
        trackLength = self._getConfig("trackLength", 20)
        print(f"\n=== KIERROS {self._roundNumber} ===")
        for horse in self.horses:
            if horse["status"] != "racing":
                label = "[KUOLI]" if horse["status"] == "dead" else "[DNF]"
                print(f"{horse['name']:<{self._nameWidth()}} {label}")
                continue
            barLen = int(horse["position"] / trackLength * 22)
            barLen = max(0, min(22, barLen))
            bar = "-" * barLen + "@" + "-" * (22 - barLen)
            if horse["fightRoundsLeft"] > 0:
                opponent = self._getHorseById(horse["fightOpponent"])
                status = f"  [TAPPELU vs {opponent['name']}. {horse['fightRoundsLeft']}krt]"
            elif horse["motivatedRoundsLeft"] > 0:
                status = f"  [MOTIVOITUNUT {horse['motivatedRoundsLeft']}krt]"
            elif horse["confusedRoundsLeft"] > 0:
                status = f"  [SEKAISIN {horse['confusedRoundsLeft']}krt]"
            elif horse["tiredRoundsLeft"] > 0:
                status = f"  [VÄSYNYT {horse['tiredRoundsLeft']}krt]"
            else:
                status = ""
            print(f"{horse['name']:<{self._nameWidth()}} [{bar}]  {horse['position']}/{trackLength}{status}")

    def _nameWidth(self) -> int:
        return max((len(h["name"]) for h in self.horses), default=14)

    def _getConfig(self, key, default):
        return self.config.get(key, default)

    def _getHorseById(self, horseId: int) -> dict:
        return next(h for h in self.horses if h["id"] == horseId)

    def _findPlayer(self, name: str):
        for p in self.players:
            if p.getName().lower() == name.lower():
                return p
        return None