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
    RaceStartEvent, BetsPlacedEvent, RaceRoundEvent, RaceFinishedEvent,
    TiebreakStartEvent, TiebreakRoundEvent, TiebreakEliminationEvent, TiebreakWinnerEvent,
    HorseEventFiredEvent, RavitBettorDrinkEvent,
)
from games.ravitGame.horses import generateHorses, Horse
from games.ravitGame.jockeys import Jockey, dealJockeys
from games.ravitGame.ravitEvents import RavitEventsMixin
import games.ravitGame.eventTypes as ET


@dataclass
class RavitGame(RavitEventsMixin, Game):
    """Drinking-game horse race. Call playRound() to run one full game."""

    gameTitle: str = "Ravit"
    config: dict = field(default_factory=dict)
    horses: list[Horse] = field(default_factory=list)
    bets: list[dict] = field(default_factory=list)
    _roundNumber: int = field(default=0, init=False, repr=False)
    _roundEvents: list = field(default_factory=list, init=False, repr=False)
    _eventedThisRound: set = field(default_factory=set, init=False, repr=False)
    _jockeyMap: dict = field(default_factory=dict, init=False, repr=False)

    def playRound(self) -> None:
        self.emit(GameStartEvent([p.getName() for p in self.players]))
        self._setupHorses()
        self._assignJockeys()
        self._bettingPhase()
        self._raceLoop()
        self._resolveFinish()
        self._drinkResolution()

    def _setupHorses(self) -> None:
        count = self._getConfig("horseCount", 4)
        self.horses = generateHorses(count)

    def _assignJockeys(self) -> None:
        jockeys = dealJockeys(len(self.horses))
        for horse, jockey in zip(self.horses, jockeys):
            self._jockeyMap[horse.id] = jockey
            jockey.applyToHorse(horse)

    def _jockeyForHorse(self, horse: Horse) -> Jockey | None:
        return self._jockeyMap.get(horse.id)

    def _bettingPhase(self) -> None:
        self.emit(RaceStartEvent(
            players=[p.getName() for p in self.players],
            horses=[h.toDict() for h in self.horses],
        ))

        debug = self._getConfig("debug", False)
        nw = self._nameWidth()
        maxBet = self._getConfig("maxBet", 5)

        print("\n=== VEDONLYÖNTI ===\n")
        print(f"{'':>{3 + nw}}  kerroin  jockey")
        for h in self.horses:
            j = self._jockeyMap.get(h.id)
            jStr = f"  [{j.name}]" if j else ""
            stats = f"  [nop:{h.speed} kes:{h.endurance} tur:{h.luck}]" if debug else ""
            print(f"  {h.id}. {h.name:<{nw}}  x{h.odds}{jStr}{stats}")

        print()
        for h in self.horses:
            j = self._jockeyMap.get(h.id)
            if j:
                print(f"  {j.name}: {j.description}")
        print()

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

        jockeyAssignments = [
            {"horseName": h.name, "jockeyName": j.name, "jockeyDescription": j.description}
            for h in self.horses
            if (j := self._jockeyMap.get(h.id))
        ]
        self.emit(BetsPlacedEvent(
            horses=[h.toDict() for h in self.horses],
            bets=list(self.bets),
            jockeys=jockeyAssignments,
        ))

    def _raceLoop(self) -> None:
        trackLength = self._getConfig("trackLength", 20)
        print("\n=== STARTTIVIIVA ===")
        for horse in self.horses:
            bar = "@" + "-" * 22
            print(f"{horse.name:<{self._nameWidth()}} [{bar}]  0/{trackLength}")
        startPositions = [
            {"id": h.id, "name": h.name, "position": 0, "status": "racing",
             "tiredRoundsLeft": 0, "stumbleRoundsLeft": 0, "motivatedRoundsLeft": 0,
             "fightRoundsLeft": 0, "confusedRoundsLeft": 0}
            for h in self.horses
        ]
        self.emit(RaceRoundEvent(roundNumber=0, trackLength=trackLength, positions=startPositions, raceEvents=[]))
        input("\nKilpailu alkaa! Paina Enter edetäksesi.\n")
        while True:
            self._roundNumber += 1
            self._runOneRound()
            aliveHorses = [h for h in self.horses if h.status == "racing"]
            if not aliveHorses or any(h.position >= trackLength for h in aliveHorses):
                break
            input("\nPaina Enter jatkaaksesi...")

    def _runOneRound(self) -> None:
        self._roundEvents = []
        self._eventedThisRound = set()
        self._resolveFights()
        self._checkNewFights()
        for horse in self.horses:
            if horse.status != "racing" or horse.fightRoundsLeft > 0:
                continue
            self._tryFireEvent(horse)
            if horse.status == "racing":
                self._moveHorse(horse)
        trackLength = self._getConfig("trackLength", 20)
        positions = [
            {
                "id": h.id, "name": h.name, "position": h.position,
                "status": h.status,
                "tiredRoundsLeft": h.tiredRoundsLeft,
                "stumbleRoundsLeft": h.stumbleRoundsLeft,
                "motivatedRoundsLeft": h.motivatedRoundsLeft,
                "fightRoundsLeft": h.fightRoundsLeft,
                "confusedRoundsLeft": h.confusedRoundsLeft,
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
        free = [h for h in self.horses if h.status == "racing" and h.fightRoundsLeft == 0 and h.position > 5]
        fighting = set()
        for i, h1 in enumerate(free):
            if h1.id in fighting:
                continue
            for h2 in free[i + 1:]:
                if h2.id in fighting:
                    continue
                j1 = self._jockeyForHorse(h1)
                j2 = self._jockeyForHorse(h2)
                if abs(h1.position - h2.position) <= 1 and random.random() < fightChance \
                        and not (j1 and j1.immuneToFights) and not (j2 and j2.immuneToFights):
                    rounds = random.randint(1, 3)
                    h1.fightRoundsLeft = rounds
                    h1.fightOpponent = h2.id
                    h2.fightRoundsLeft = rounds
                    h2.fightOpponent = h1.id
                    fighting.add(h1.id)
                    fighting.add(h2.id)
                    self._eventedThisRound.add(h1.id)
                    self._eventedThisRound.add(h2.id)
                    detail = f"{h1.name} ja {h2.name} tappelevat!"
                    print(f"  *** {detail}")
                    self._roundEvents.append({"horseName": h1.name, "eventType": ET.FIGHT_START, "detail": detail})
                    self.emit(HorseEventFiredEvent(
                        roundNumber=self._roundNumber,
                        horseId=h1.id,
                        horseName=h1.name,
                        eventType=ET.FIGHT_START,
                        detail=detail,
                    ))
                    break

    def _resolveFights(self) -> None:
        processed = set()
        for horse in self.horses:
            if horse.status != "racing" or horse.fightRoundsLeft <= 0 or horse.id in processed:
                continue
            opponent = self._getHorseById(horse.fightOpponent)
            processed.add(horse.id)
            processed.add(opponent.id)
            horse.fightRoundsLeft -= 1
            opponent.fightRoundsLeft -= 1
            if horse.fightRoundsLeft <= 0:
                self._eventedThisRound.add(horse.id)
                self._eventedThisRound.add(opponent.id)
                if opponent.status != "racing":
                    horse.fightOpponent = None
                else:
                    self._resolveFightBetween(horse, opponent)

    def _drinkBettorOfHorse(self, horse: Horse, amount: int, reason: str) -> None:
        """Find the bettor of a horse, assign drinks, and emit bettor drink events."""
        bet = next((b for b in self.bets if b["horseId"] == horse.id), None)
        if not bet:
            return
        player = self._findPlayer(bet["player"])
        if not player:
            return
        player.addDrinks(amount)
        print(f"  >>> {player.getName()} juo {amount}! ({horse.name}: {reason})")
        self.emit(DrinkEvent(player=player.getName(), amount=amount, reason=reason))
        scores = [{"name": p.getName(), "drank": p.getDrinksTaken()} for p in self.players]
        self.emit(RavitBettorDrinkEvent(
            playerName=player.getName(),
            horseName=horse.name,
            amount=amount,
            reason=reason,
            scores=scores,
        ))

    def _resolveFightBetween(self, h1: Horse, h2: Horse) -> None:
        """Determine fight winner by strength ratio; loser dies, winner loses 1 in all stats."""
        total = h1.fightStrength + h2.fightStrength
        winner, loser = (h1, h2) if random.random() < h1.fightStrength / total else (h2, h1)
        loser.status = "dead"
        winner.fightRoundsLeft = 0
        winner.fightOpponent = None
        for stat in ("speed", "endurance", "luck"):
            setattr(winner, stat, max(1, getattr(winner, stat) - 1))
        detail = (
            f"Tappelu ohi! {winner.name} voitti — {loser.name} kuoli! "
            f"{winner.name} on loukkaantunut (kaikki tilastot -1)!"
        )
        print(f"  *** {detail}")
        self._roundEvents.append({"horseName": winner.name, "eventType": ET.FIGHT_WIN, "detail": detail})
        self.emit(HorseEventFiredEvent(
            roundNumber=self._roundNumber,
            horseId=loser.id,
            horseName=loser.name,
            eventType=ET.FIGHT_DEATH,
            detail=detail,
        ))
        self._drinkBettorOfHorse(loser, 2, "hevonen kuoli taistelussa")

    def _tiebreakFight(self, tied: list) -> Horse:
        """Run interactive multi-round combat between tied finishers; returns the winner or None if all die."""
        print("\n" + "=" * 40)
        print("  *** TASAPELI! VALMISTAUTUKAA LOPPUKAMPPAILUUN! ***")
        print("=" * 40)
        names = ", ".join(h.name for h in tied)
        print(f"\n{names} ylittävät maaliviivan samaan aikaan!")
        self.emit(TiebreakStartEvent(
            combatants=[{
                "id": h.id, "name": h.name, "odds": h.odds,
                "health": h.fightMaxHealth, "maxHealth": h.fightMaxHealth,
                "strength": h.fightStrength,
            } for h in tied]
        ))

        combatants = list(tied)
        for h in combatants:
            h.fightHealth = h.fightMaxHealth

        self._printCombatantBars(combatants)
        input("\nPaina Enter aloittaaksesi taistelun...")

        roundNum = 0
        while len(combatants) > 1:
            roundNum += 1
            print(f"\n  --- TAISTELUKIERROS {roundNum} ---")
            input("  Paina Enter...")

            thisRound = list(combatants)
            for attacker in thisRound:
                targets = [h for h in thisRound if h.id != attacker.id]
                target = random.choice(targets)
                damage = random.randint(1, attacker.fightStrength)
                target.fightHealth = max(0, target.fightHealth - damage)
                print(f"  {attacker.name:<12} -> {target.name}: -{damage} HP")

            eliminated = [h for h in thisRound if h.fightHealth <= 0]
            combatants = [h for h in thisRound if h.fightHealth > 0]

            self._printCombatantBars(thisRound)

            allState = [
                {"name": h.name, "health": h.fightHealth,
                 "maxHealth": h.fightMaxHealth, "strength": h.fightStrength}
                for h in thisRound
            ]
            self.emit(TiebreakRoundEvent(roundNumber=roundNum, combatants=allState))

            for loser in eliminated:
                loser.status = "dead"
                print(f"\n  *** {loser.name} kuoli!")
                self.emit(TiebreakEliminationEvent(
                    loserName=loser.name,
                    remaining=[h.name for h in combatants],
                    combatants=allState,
                ))

            if not combatants:
                print(f"\n{'*' * 40}")
                print("  KAIKKI KAATUIVAT! Ei voittajaa.")
                print(f"{'*' * 40}\n")
                return None

        winner = combatants[0]
        print(f"\n{'*' * 40}")
        print(f"  {winner.name.upper()} VOITTAA LOPPUKAMPPAILUN!")
        print(f"{'*' * 40}\n")
        self.emit(TiebreakWinnerEvent(
            winnerName=winner.name,
            health=winner.fightHealth,
            maxHealth=winner.fightMaxHealth,
            strength=winner.fightStrength,
        ))
        return winner

    def _printCombatantBars(self, combatants: list) -> None:
        print()
        for h in combatants:
            hp = h.fightHealth
            maxHp = h.fightMaxHealth
            filled = int(hp / maxHp * 16) if maxHp > 0 else 0
            bar = "█" * filled + "░" * (16 - filled)
            status = " [KUOLI]" if hp <= 0 else f"  (v:{h.fightStrength})"
            print(f"  {h.name:<12} [{bar}] {hp:>3}/{maxHp}{status}")

    def _resolveFinish(self) -> None:
        """Rank horses, trigger tiebreak if top positions are within 1 tile, emit RaceFinishedEvent."""
        trackLength = self._getConfig("trackLength", 20)
        aliveHorses = [h for h in self.horses if h.status == "racing"]
        outHorses = [h for h in self.horses if h.status != "racing"]

        aliveHorses.sort(key=lambda h: h.position, reverse=True)

        if aliveHorses:
            topPos = aliveHorses[0].position
            closeFinish = [h for h in aliveHorses if topPos - h.position <= 1]
            if len(closeFinish) > 1:
                winner = self._tiebreakFight(closeFinish)
                if winner is not None:
                    aliveHorses = [winner] + [h for h in aliveHorses if h.id != winner.id and h.status == "racing"]
                    outHorses = [h for h in self.horses if h.status != "racing"]

        finalPositions = []
        for place, horse in enumerate(aliveHorses, start=1):
            displayPos = horse.position if place == 1 else min(horse.position, trackLength - 1)
            finalPositions.append({
                "horseId": horse.id,
                "horseName": horse.name,
                "position": displayPos,
                "place": place,
                "status": "racing",
            })

        nextPlace = len(aliveHorses) + 1
        dnfHorses = sorted([h for h in outHorses if h.status == "dnf"], key=lambda h: -h.position)
        deadHorses = sorted([h for h in outHorses if h.status == "dead"], key=lambda h: -h.position)
        for horse in dnfHorses + deadHorses:
            finalPositions.append({
                "horseId": horse.id,
                "horseName": horse.name,
                "position": horse.position,
                "place": nextPlace,
                "status": horse.status,
            })
            nextPlace += 1

        print("\n=== LOPPUTULOS ===")
        for fp in finalPositions:
            if fp["status"] == "racing":
                print(f"{fp['place']}. {fp['horseName']:<{self._nameWidth()}} {fp['position']}/{trackLength}")
            else:
                label = "[KUOLI]" if fp["status"] == "dead" else "[DNF]"
                print(f"   {label} {fp['horseName']}")

        self.emit(RaceFinishedEvent(
            roundNumber=self._roundNumber,
            finalPositions=finalPositions,
        ))

    def _drinkResolution(self) -> None:
        """Assign drinks: dead/DNF bettors drink double, winner gives to last-place bettors, rest drink bet."""
        aliveHorses = [h for h in self.horses if h.status == "racing"]
        if not aliveHorses:
            for bet in self.bets:
                player = self._findPlayer(bet["player"])
                if player:
                    horse = self._getHorseById(bet["horseId"])
                    reason = "hevonen kuoli" if horse.status == "dead" else "hevonen ei pystynyt jatkamaan"
                    player.addDrinks(bet["amount"] * 2)
                    self.emit(DrinkEvent(player=bet["player"], amount=bet["amount"] * 2, reason=reason))
        else:
            winnerId = max(aliveHorses, key=lambda h: h.position).id
            minPos = min(h.position for h in aliveHorses)
            lastPlaceIds = {h.id for h in aliveHorses if h.position == minPos}

            for bet in self.bets:
                player = self._findPlayer(bet["player"])
                if not player:
                    continue
                horse = self._getHorseById(bet["horseId"])
                if horse.status != "racing":
                    reason = "hevonen kuoli" if horse.status == "dead" else "hevonen ei pystynyt jatkamaan"
                    player.addDrinks(bet["amount"] * 2)
                    self.emit(DrinkEvent(player=bet["player"], amount=bet["amount"] * 2, reason=reason))
                elif horse.id == winnerId:
                    if lastPlaceIds:
                        player.pendingGive += math.ceil(bet["amount"] * horse.odds)
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

    def _moveHorse(self, horse: Horse) -> None:
        """Advance horse one round, applying stamina depletion, tired/stumble/confused/motivated effects."""
        trackLength = self._getConfig("trackLength", 20)
        if horse.stumbleRoundsLeft > 0:
            horse.stumbleRoundsLeft -= 1
            if horse.motivatedRoundsLeft > 0:
                horse.motivatedRoundsLeft -= 1
            if horse.tiredRoundsLeft > 0:
                horse.tiredRoundsLeft -= 1
            if horse.confusedRoundsLeft > 0:
                horse.confusedRoundsLeft -= 1
            return

        baseRoll = random.randint(0, 2)
        effectiveSpeed = horse.speed
        wasTired = horse.tiredRoundsLeft > 0
        if wasTired:
            effectiveSpeed = max(1, effectiveSpeed - 1)
            horse.tiredRoundsLeft -= 1
        if horse.motivatedRoundsLeft > 0:
            effectiveSpeed += 1
            horse.motivatedRoundsLeft -= 1

        if horse.confusedRoundsLeft > 0:
            horse.confusedRoundsLeft -= 1
            horse.position = max(0, horse.position - (effectiveSpeed + baseRoll))
            return

        move = effectiveSpeed + baseRoll
        if horse.position >= trackLength // 2 and horse.endurance <= 2:
            move = max(1, move - 1)

        horse.position = min(horse.position + move, trackLength)

        if not wasTired:
            horse.staminaLeft -= 1
            if horse.staminaLeft <= 0:
                horse.tiredRoundsLeft = 2
                horse.staminaLeft = max(1, horse.endurance * 2)

    def _printTrack(self) -> None:
        trackLength = self._getConfig("trackLength", 20)
        print(f"\n=== KIERROS {self._roundNumber} ===")
        for horse in self.horses:
            if horse.status != "racing":
                label = "[KUOLI]" if horse.status == "dead" else "[DNF]"
                print(f"{horse.name:<{self._nameWidth()}} {label}")
                continue
            barLen = max(0, min(22, int(horse.position / trackLength * 22)))
            bar = "-" * barLen + "@" + "-" * (22 - barLen)
            if horse.fightRoundsLeft > 0:
                opponent = self._getHorseById(horse.fightOpponent)
                status = f"  [TAPPELU vs {opponent.name}. {horse.fightRoundsLeft}krt]"
            elif horse.motivatedRoundsLeft > 0:
                status = f"  [MOTIVOITUNUT {horse.motivatedRoundsLeft}krt]"
            elif horse.confusedRoundsLeft > 0:
                status = f"  [SEKAISIN {horse.confusedRoundsLeft}krt]"
            elif horse.tiredRoundsLeft > 0:
                status = f"  [VÄSYNYT {horse.tiredRoundsLeft}krt]"
            else:
                status = ""
            print(f"{horse.name:<{self._nameWidth()}} [{bar}]  {horse.position}/{trackLength}{status}")

    def _nameWidth(self) -> int:
        return max((len(h.name) for h in self.horses), default=14)

    def _getConfig(self, key, default):
        return self.config.get(key, default)

    def _getHorseById(self, horseId: int) -> Horse:
        return next(h for h in self.horses if h.id == horseId)

    def _findPlayer(self, name: str):
        for p in self.players:
            if p.getName().lower() == name.lower():
                return p
        return None
