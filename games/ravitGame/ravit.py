import random
import math
from dataclasses import dataclass, field
from core.game import Game
from core.events import (
    GameStartEvent, GameEndEvent,
    DrinkEvent,
    RaceStartEvent, RaceRoundEvent, HorseEventFiredEvent, RaceFinishedEvent,
    TiebreakStartEvent, TiebreakEliminationEvent, TiebreakWinnerEvent,
)
from games.ravitGame.horses import generateHorses


@dataclass
class RavitGame(Game):
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
            stats = f"  [nop:{h['speed']} kes:{h['endurance']} tur:{h['luck']}]" if debug else ""
            print(f"{h['id']}. {h['name']:<14}  kerroin: x{h['odds']}{stats}")
        print()

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

        self.emit(RaceStartEvent(
            players=[p.getName() for p in self.players],
            horses=[dict(h) for h in self.horses],
            bets=list(self.bets),
        ))

    def _raceLoop(self) -> None:
        trackLength = self._getConfig("trackLength", 20)
        print("\nKilpailu alkaa! Paina Enter edetäksesi kierros kerrallaan.\n")
        input()
        while True:
            self._roundNumber += 1
            self._runOneRound()
            aliveHorses = [h for h in self.horses if h["alive"]]
            if not aliveHorses or any(h["position"] >= trackLength for h in aliveHorses):
                break
            input("\nPaina Enter jatkaaksesi...")

    def _runOneRound(self) -> None:
        self._roundEvents = []
        self._resolveFights()
        self._checkNewFights()
        for horse in self.horses:
            if not horse["alive"] or horse["fightRoundsLeft"] > 0:
                continue
            self._tryFireEvent(horse)
            if horse["alive"]:
                self._moveHorse(horse)
        trackLength = self._getConfig("trackLength", 40)
        positions = [
            {
                "id": h["id"], "name": h["name"], "position": h["position"],
                "alive": h["alive"], "tiredRoundsLeft": h["tiredRoundsLeft"],
                "stumbleRoundsLeft": h["stumbleRoundsLeft"],
                "motivatedRoundsLeft": h["motivatedRoundsLeft"],
                "fightRoundsLeft": h["fightRoundsLeft"],
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
        free = [h for h in self.horses if h["alive"] and h["fightRoundsLeft"] == 0 and h["position"] > 5]
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
                    detail = f"{h1['name']} ja {h2['name']} aloittavat tappelun! ({rounds} kierrosta)"
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
            if not horse["alive"] or horse["fightRoundsLeft"] <= 0 or horse["id"] in processed:
                continue
            opponent = self._getHorseById(horse["fightOpponent"])
            processed.add(horse["id"])
            processed.add(opponent["id"])
            horse["fightRoundsLeft"] -= 1
            opponent["fightRoundsLeft"] -= 1
            if horse["fightRoundsLeft"] <= 0:
                if not opponent["alive"]:
                    horse["fightOpponent"] = None
                else:
                    self._resolveFightBetween(horse, opponent)

    def _resolveFightBetween(self, h1: dict, h2: dict) -> None:
        total = h1["fightStrength"] + h2["fightStrength"]
        winner, loser = (h1, h2) if random.random() < h1["fightStrength"] / total else (h2, h1)
        loser["alive"] = False
        winner["fightRoundsLeft"] = 0
        winner["fightOpponent"] = None
        for stat in ("speed", "endurance", "luck"):
            winner[stat] = max(1, winner[stat] - 1)
        detail = (
            f"Tappelu ohi! {winner['name']} voitti — {loser['name']} kaatuu! "
            f"{winner['name']} on loukkaantunut (kaikki tilastot -1)!"
        )
        print(f"  *** {detail}")
        self._roundEvents.append({"horseName": winner["name"], "eventType": "fight_win", "detail": detail})
        self.emit(HorseEventFiredEvent(
            roundNumber=self._roundNumber,
            horseId=loser["id"],
            horseName=loser["name"],
            eventType="death",
            detail=detail,
        ))

    def _tiebreakFight(self, tied: list) -> dict:
        print("\n" + "=" * 40)
        print("  *** TASAPELI! EEPINEN LOPPUKAMPPAILU! ***")
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

        round_num = 0
        while len(combatants) > 1:
            round_num += 1
            print(f"\n  --- TAISTELUKIERROS {round_num} ---")
            input("  Paina Enter...")

            this_round = list(combatants)
            for attacker in this_round:
                targets = [h for h in this_round if h["id"] != attacker["id"]]
                target = random.choice(targets)
                damage = random.randint(1, attacker["fightStrength"])
                target["fightHealth"] = max(0, target["fightHealth"] - damage)
                print(f"  {attacker['name']:<12} -> {target['name']}: -{damage} HP")

            self._printCombatantBars(this_round)

            eliminated = [h for h in this_round if h["fightHealth"] <= 0]
            combatants = [h for h in this_round if h["fightHealth"] > 0]

            if not combatants:
                survivor = max(eliminated, key=lambda h: h["fightStrength"])
                survivor["fightHealth"] = 1
                combatants = [survivor]
                eliminated = [h for h in eliminated if h["id"] != survivor["id"]]

            all_state = [
                {"name": h["name"], "health": h["fightHealth"],
                 "maxHealth": h["fightMaxHealth"], "strength": h["fightStrength"]}
                for h in this_round
            ]
            for loser in eliminated:
                print(f"\n  *** {loser['name']} kaatuu!")
                self.emit(TiebreakEliminationEvent(
                    loserName=loser["name"],
                    remaining=[h["name"] for h in combatants],
                    combatants=all_state,
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
            status = " [KAATUI]" if hp <= 0 else f"  (v:{h['fightStrength']})"
            print(f"  {h['name']:<12} [{bar}] {hp:>3}/{maxHp}{status}")

    def _resolveFinish(self) -> None:
        trackLength = self._getConfig("trackLength", 20)
        aliveHorses = [h for h in self.horses if h["alive"]]
        deadHorses = [h for h in self.horses if not h["alive"]]

        aliveHorses.sort(key=lambda h: h["position"], reverse=True)

        if aliveHorses:
            topPos = aliveHorses[0]["position"]
            tiedFirst = [h for h in aliveHorses if h["position"] == topPos]
            if len(tiedFirst) > 1:
                winner = self._tiebreakFight(tiedFirst)
                aliveHorses = [winner] + [h for h in aliveHorses if h["id"] != winner["id"]]

        deadPenalty = len(self.horses) + 1

        finalPositions = []
        for place, horse in enumerate(aliveHorses, start=1):
            finalPositions.append({
                "horseId": horse["id"],
                "horseName": horse["name"],
                "position": horse["position"],
                "place": place,
                "alive": True,
            })
        for horse in deadHorses:
            finalPositions.append({
                "horseId": horse["id"],
                "horseName": horse["name"],
                "position": horse["position"],
                "place": deadPenalty,
                "alive": False,
            })

        print("\n=== LOPPUTULOS ===")
        for fp in finalPositions:
            if fp["alive"]:
                print(f"{fp['place']}. {fp['horseName']:<14} {fp['position']}/{trackLength} ruutua")
            else:
                print(f"   [KUOLLUT] {fp['horseName']}")

        self.emit(RaceFinishedEvent(
            roundNumber=self._roundNumber,
            finalPositions=finalPositions,
        ))

    def _drinkResolution(self) -> None:
        aliveHorses = [h for h in self.horses if h["alive"]]
        if not aliveHorses:
            # Edge case: all dead — no winner
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
                if not horse["alive"]:
                    player.addDrinks(bet["amount"] * 2)
                    self.emit(DrinkEvent(player=bet["player"], amount=bet["amount"] * 2, reason="hevonen kuoli"))
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
        trackLength = self._getConfig("trackLength", 20)
        if horse["stumbleRoundsLeft"] > 0:
            horse["stumbleRoundsLeft"] -= 1
            return

        baseRoll = random.randint(0, 2)
        effectiveSpeed = horse["speed"]
        if horse["tiredRoundsLeft"] > 0:
            effectiveSpeed = max(1, effectiveSpeed - 1)
            horse["tiredRoundsLeft"] -= 1
        if horse["motivatedRoundsLeft"] > 0:
            effectiveSpeed += 1
            horse["motivatedRoundsLeft"] -= 1

        move = effectiveSpeed + baseRoll
        halfway = trackLength // 2
        if horse["position"] >= halfway:
            if horse["endurance"] >= 4:
                move += 1
            elif horse["endurance"] <= 2:
                move = max(1, move - 1)

        horse["position"] = min(horse["position"] + move, trackLength)

    def _tryFireEvent(self, horse: dict) -> None:
        eventChance = self._getConfig("eventChance", 0.15)
        luckMultiplier = (6 - horse["luck"]) / 3.0
        adjustedChance = min(eventChance * luckMultiplier, 0.95)
        if random.random() >= adjustedChance:
            return

        eventType = random.choices(
            ["death", "backwards", "boost", "tired", "stumble", "motivated"],
            weights=[1, 3, 4, 3, 3, 4],
        )[0]

        trackLength = self._getConfig("trackLength", 20)

        if eventType == "death":
            horse["alive"] = False
            detail = f"{horse['name']} kaatuu ja poistuu kilpailusta!"
        elif eventType == "backwards":
            tiles = random.randint(2, 3)
            horse["position"] = max(0, horse["position"] - tiles)
            detail = f"{horse['name']} kompastuu ja peruuttaa {tiles} ruutua!"
        elif eventType == "boost":
            horse["position"] = min(horse["position"] + 3, trackLength)
            detail = f"{horse['name']} saa vauhtia ja lentää 3 ruutua eteenpäin!"
        elif eventType == "tired":
            horse["tiredRoundsLeft"] = 2
            detail = f"{horse['name']} väsyy — nopeus -1 seuraavat 2 kierrosta!"
        elif eventType == "stumble":
            horse["stumbleRoundsLeft"] = 1
            detail = f"{horse['name']} kompuroi — ohittaa seuraavan kierroksen!"
        else:
            rounds = random.randint(1, 3)
            horse["motivatedRoundsLeft"] = rounds
            detail = f"{horse['name']} saa motivaatiota — nopeus +1 seuraavat {rounds} kierrosta!"

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
            if not horse["alive"]:
                print(f"{horse['name']:<14} [KUOLLUT]")
                continue
            barLen = int(horse["position"] / trackLength * 22)
            barLen = max(0, min(22, barLen))
            bar = "-" * barLen + "@" + "-" * (22 - barLen)
            if horse["fightRoundsLeft"] > 0:
                opponent = self._getHorseById(horse["fightOpponent"])
                status = f"  [TAPPELU vs {opponent['name']} — {horse['fightRoundsLeft']}krt]"
            elif horse["motivatedRoundsLeft"] > 0:
                status = f"  [MOTIVOITUNUT {horse['motivatedRoundsLeft']}krt]"
            elif horse["tiredRoundsLeft"] > 0:
                status = f"  [VÄSYNYT {horse['tiredRoundsLeft']}krt]"
            else:
                status = ""
            print(f"{horse['name']:<14} [{bar}]  {horse['position']}/{trackLength}{status}")

    def _getConfig(self, key, default):
        return self.config.get(key, default)

    def _getHorseById(self, horseId: int) -> dict:
        return next(h for h in self.horses if h["id"] == horseId)

    def _betsForHorse(self, horseId: int) -> list:
        return [b for b in self.bets if b["horseId"] == horseId]

    def _findPlayer(self, name: str):
        for p in self.players:
            if p.getName().lower() == name.lower():
                return p
        return None
