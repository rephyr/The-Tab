"""
TaskGame: a turn-based drinking game where each turn a random task is drawn.
Tasks can target a single player, multiple random players, or everyone.
"""
from core.game import Game
from core.events import GameStartEvent, GameEndEvent, TaskDrawEvent, RouletteResultEvent, TaskDrinkSummaryEvent, TaskChainStartEvent
from dataclasses import dataclass, field
from games.taskGame.tasks import TASKS
from games.taskGame.penalties import drawPenalty
import random

# Each task has:
#   title       -- short name printed in large text on the receipt
#   description -- the rule or challenge text
#   players     -- how many players are picked: 1, 2, N, or "all"
#                  1 targets the drawing player themselves

@dataclass
class TaskGame(Game):
    """
    Task-based drinking game. Players take turns drawing a random task.
    The task defines how many players are involved.
    """
    gameTitle: str = "TaskGame"

    config: dict = field(default_factory=dict)
    activePairs: list = field(default_factory=list)   # [[player1, player2]]
    activeHuoras: list = field(default_factory=list)  # [[master, huora]]
    immunePlayers: list = field(default_factory=list) # players with one pending immunity
    activePenalties: list = field(default_factory=list)  # [{"player": Player, "title": str, "turnsLeft": int}]
    doubleNext: bool = False
    chainStep: int = 0       # 0 = no chain active; N>0 = next player drinks N*3
    chainStepsLeft: int = 0  # turns remaining in the chain

    def _buildPool(self) -> list:
        """Build a shuffled deck with each task repeated according to its rarity and config."""
        commonCount = self.config.get("commonCount", 4)
        specialCount = self.config.get("specialCount", 2)
        deck = []
        for task in TASKS:
            count = specialCount if task.get("rarity") == "special" else commonCount
            deck.extend([task] * count)
        random.shuffle(deck)
        return deck

    def playRound(self) -> None:
        """Run a full game: players take turns drawing tasks until someone quits."""
        self.emit(GameStartEvent([p.getName() for p in self.players]))

        taskPool = self._buildPool()
        deckTotal = len(taskPool)

        if not taskPool:
            print("Ei tehtäviä määritelty.")
            return

        running = True
        while running:
            for player in self.players:
                self._tickPenalties()
                self._showLinks()
                while True:
                    cmd = input(f"\n{player.getName()}n vuoro -- paina Enter nostaaksesi (d = pakka): ").strip().lower()
                    if cmd == "d":
                        print(f"Kortteja jäljellä: {len(taskPool)}/{deckTotal}")
                    else:
                        break

                self._applyChain(player)

                if not taskPool:
                    running = False
                    break

                task = taskPool.pop()

                targets = self._resolveTargets(task["players"], player)
                targetNames = ", ".join(p.getName() for p in targets)

                print(f"\n>>> {task['title']}")
                print(f"Pelaajat: {targetNames}")
                print(task["description"])

                drinkType = task.get("drinkType", "social")

                if drinkType == "chain":
                    self.emit(TaskChainStartEvent(
                        drawer=player.getName(),
                        title=task["title"],
                        description=task["description"],
                        assignments=self._calcChainAssignments(player, task.get("drinks", 3)),
                    ))
                else:
                    self.emit(TaskDrawEvent(
                        drawer=player.getName(),
                        title=task["title"],
                        description=task["description"],
                        targets=[p.getName() for p in targets],
                    ))

                beforeDrinks = {p.getId(): p.getDrinksTaken() for p in self.players}
                beforePending = {p.getId(): p.pendingGive for p in self.players}

                self._handlePostTask(task, targets, player)

                if drinkType != "chain":
                    deltas = [
                        {"name": p.getName(),
                         "drank": p.getDrinksTaken() - beforeDrinks[p.getId()],
                         "toGive": p.pendingGive - beforePending[p.getId()]}
                        for p in self.players
                        if p.getDrinksTaken() > beforeDrinks[p.getId()] or p.pendingGive > beforePending[p.getId()]
                    ]
                    if deltas:
                        self.emit(TaskDrinkSummaryEvent(deltas))

                while True:
                    raw = input("\nJatketaan? (Enter = kyllä, quit = lopeta, j = kirjaa juomat): ").strip().lower()
                    if raw == "quit":
                        running = False
                        break
                    if raw == "j":
                        self._interactiveAssignDrinks()
                    elif not raw:
                        break
                    else:
                        print("  (Enter = jatka, quit = lopeta, j = kirjaa juomat)")
                if not running:
                    break

        self._interactiveGivePhase()

        self.emit(GameEndEvent([
            {"name": p.getName(), "drinksTaken": p.getDrinksTaken(), "drinksToGive": p.drinksToGive}
            for p in self.players
        ]))

        print("\n" + "=" * 24)
        print("LOPPULASKU")
        print("=" * 24)
        for p in self.players:
            print(f"{p.getName()}: joi {p.getDrinksTaken()} | antoi {p.drinksToGive}")
        print("=" * 24)

    def _resolveTargets(self, playerCount, drawer):
        """Return the list of players targeted by a task."""
        if playerCount == "all":
            return list(self.players)
        if playerCount == 1:
            return [drawer]
        return self._pickRandom(playerCount, exclude=drawer)

    def _pickRandom(self, count: int, exclude=None):
        """Return `count` randomly chosen players, excluding the given player if provided."""
        pool = [p for p in self.players if p != exclude]
        return random.sample(pool, min(count, len(pool)))

    def _assignDrinks(self, player, amount: int, _visited=None) -> None:
        """Add drinks to a player and propagate through active links.

        Huora chains are fully recursive (A→B→C). Pairs also propagate recursively.
        The visited set prevents any back-propagation or loops.
        """
        if _visited is None:
            _visited = set()
        if id(player) in _visited:
            return

        if player in self.immunePlayers:
            self.immunePlayers.remove(player)
            print(f"  {player.getName()} käytti immuniteetin! (ei juo)")
            _visited.add(id(player))
            return

        player.addDrinks(amount)
        _visited.add(id(player))

        for p1, p2 in self.activePairs:
            if player == p1 and id(p2) not in _visited:
                print(f"  {p2.getName()} juo myös {amount} (pari)")
                self._assignDrinks(p2, amount, _visited)
            elif player == p2 and id(p1) not in _visited:
                print(f"  {p1.getName()} juo myös {amount} (pari)")
                self._assignDrinks(p1, amount, _visited)

        for master, huora in self.activeHuoras:
            if player == master and id(huora) not in _visited:
                print(f"  {huora.getName()} juo myös {amount} (huora)")
                self._assignDrinks(huora, amount, _visited)

    def _traceCascade(self, player, amount: int, visited=None) -> list:
        """Simulate huora/pair propagation without modifying state."""
        if visited is None:
            visited = set()
        if id(player) in visited:
            return []
        visited.add(id(player))
        result = []
        for p1, p2 in self.activePairs:
            if player == p1 and id(p2) not in visited:
                result.append({"name": p2.getName(), "amount": amount, "reason": "pari"})
                result.extend(self._traceCascade(p2, amount, visited))
            elif player == p2 and id(p1) not in visited:
                result.append({"name": p1.getName(), "amount": amount, "reason": "pari"})
                result.extend(self._traceCascade(p1, amount, visited))
        for master, huora in self.activeHuoras:
            if player == master and id(huora) not in visited:
                result.append({"name": huora.getName(), "amount": amount, "reason": "huora"})
                result.extend(self._traceCascade(huora, amount, visited))
        return result

    def _calcChainAssignments(self, drawer, baseAmount: int) -> list:
        """Calculate chain drink amounts for all players in turn order, including cascades."""
        drawerIdx = self.players.index(drawer)
        n = len(self.players)
        assignments = []
        for i in range(n):
            p = self.players[(drawerIdx + i) % n]
            amount = (i + 1) * baseAmount
            assignments.append({
                "name": p.getName(),
                "amount": amount,
                "cascades": self._traceCascade(p, amount),
            })
        return assignments

    def _findPlayer(self, name: str):
        """Return the player whose name matches (case-insensitive), or None."""
        for p in self.players:
            if p.getName().lower() == name.lower():
                return p
        return None

    def _tickPenalties(self) -> None:
        """Decrement active timed penalties and announce when they expire."""
        expired = []
        for entry in self.activePenalties:
            entry["turnsLeft"] -= 1
            if entry["turnsLeft"] <= 0:
                expired.append(entry)
            else:
                print(f"  [{entry['title']}] {entry['player'].getName()}: {entry['turnsLeft']} vuoro(a) jäljellä")
        for entry in expired:
            self.activePenalties.remove(entry)
            print(f"  [{entry['title']}] PÄÄTTYI — {entry['player'].getName()} vapautui rangaistuksesta!")

    def _applyChain(self, player) -> None:
        if self.chainStep == 0:
            return
        amount = self.chainStep * 3
        print(f"\n  KETJU: {player.getName()} juo {amount}!")
        self._assignDrinks(player, amount)
        self.chainStep += 1
        self.chainStepsLeft -= 1
        if self.chainStepsLeft <= 0:
            self.chainStep = 0
            print("  Ketju päättyi!")

    def _showLinks(self) -> None:
        """Print active pair and huora links if any exist."""
        parts = []
        for p1, p2 in self.activePairs:
            parts.append(f"{p1.getName()} <-> {p2.getName()} (pari)")
        for master, huora in self.activeHuoras:
            parts.append(f"{master.getName()} -> {huora.getName()} (huora)")
        for p in self.immunePlayers:
            parts.append(f"{p.getName()} (immuuni)")
        if self.doubleNext:
            parts.append("TUPLA aktiivinen")
        if self.chainStep > 0:
            parts.append(f"KETJU — seuraava juo {self.chainStep * 3}")
        if parts:
            print("Aktiiviset linkit: " + " | ".join(parts))

    def _handlePostTask(self, task: dict, targets: list, drawer) -> None:
        """Handle drink tracking and link updates after a task is shown."""
        drinkType = task.get("drinkType", "social")
        drinks = task.get("drinks")

        if self.doubleNext:
            self.doubleNext = False
            if drinks is not None:
                drinks = drinks * 2
                print(f"  TUPLA! Juomat tuplattu -> {drinks}")

        if drinkType == "take":
            raw = input(f"\nVahvista {drinks} juomaa {drawer.getName()}lle? (Enter = kyllä, tai kirjoita määrä): ").strip()
            amount = drinks
            if raw.isdigit():
                amount = int(raw)
            if amount > 0:
                print(f"  {drawer.getName()} juo {amount}")
                self._assignDrinks(drawer, amount)

        elif drinkType == "give":
            drawer.pendingGive += drinks
            self._interactiveGivePhase()

        elif drinkType == "social":
            if drinks is not None:
                print(f"\nJaa {drinks} juomaa:")
                self._interactiveAssignDrinks(budget=drinks)
            else:
                print("\nKirjaa juomat:")
                self._interactiveAssignDrinks()

        elif drinkType == "roulette":
            bulletIndex = random.randint(0, len(self.players) - 1)
            print(f"\n1 luoti, {len(self.players)} pelaajaa")
            for i, p in enumerate(self.players):
                input(f"  {p.getName()} -- paina Enter")
                hit = (i == bulletIndex)
                print(f"  >>> OSUMA! {p.getName()} juo {drinks}!" if hit else "  Ohi!")
                self.emit(RouletteResultEvent(player=p.getName(), hit=hit, drinks=drinks))
                if hit:
                    self._assignDrinks(p, drinks)
                    break

        elif drinkType == "chain":
            print(f"\n  {drawer.getName()} juo {drinks}!")
            self._assignDrinks(drawer, drinks)
            self.chainStep = 2
            self.chainStepsLeft = len(self.players) - 1
            print(f"  Ketju alkaa! {self.chainStepsLeft} vuoroa jäljellä.")

        elif drinkType == "special":
            key = task.get("key", "")
            if key == "immunity":
                self.immunePlayers.append(drawer)
                print(f"\n{drawer.getName()} on immuuni seuraavalle pakolliselle juomiselle.")
            elif key == "doubleNext":
                self.doubleNext = True
                print("\nSeuraavan kortin juomat tuplataan!")

        elif drinkType == "link":
            others = [p for p in self.players if p != drawer]
            if not others:
                return
            print()
            for i, p in enumerate(others, 1):
                print(f"  {i}. {p.getName()}")
            while True:
                raw = input("  Kenelle? (numero tai nimi): ").strip()
                target = self._findTargetByNameOrNumber(raw, others)
                if target:
                    break
                print("  Tuntematon pelaaja, yritä uudelleen.")
            if task["title"] == "Pari":
                self.activePairs.clear()
                self.activePairs.append([drawer, target])
                print(f"\nUusi pari: {drawer.getName()} <-> {target.getName()} (korvaa edellisen parin)")
            elif task["title"] == "Huora":
                if [drawer, target] in self.activeHuoras:
                    print(f"\n{target.getName()} on jo {drawer.getName()}n huora.")
                else:
                    self.activeHuoras.append([drawer, target])
                    print(f"\nUusi huora: {target.getName()} juo aina kun {drawer.getName()} juo")

        if task.get("penalty"):
            self._applyPenaltyToLoser()

    def _applyPenaltyToLoser(self) -> None:
        """Draw a random penalty and apply it to the player who lost the competition."""
        penalty = drawPenalty()
        print("\n--- RANGAISTUS ---")
        print(f">>> {penalty['title']}")
        print(penalty["description"])

        needsPlayer = penalty["drinkType"] in ("take", "give") or penalty.get("duration") is not None
        if not needsPlayer:
            return

        raw = input("\nKuka hävisi? (nimi tai Enter ohittaaksesi): ").strip()
        if not raw:
            return
        loser = self._findPlayer(raw)
        if not loser:
            print(f"  Pelaajaa '{raw}' ei löydy, ohitetaan.")
            return

        if penalty["drinkType"] == "take" and penalty["drinks"] is not None:
            self._assignDrinks(loser, penalty["drinks"])
        elif penalty["drinkType"] == "give" and penalty["drinks"] is not None:
            loser.pendingGive += penalty["drinks"]
            print(f"  {loser.getName()} saa antaa {penalty['drinks']} juomaa lopussa.")

        if penalty.get("duration") is not None:
            self.activePenalties.append({
                "player": loser,
                "title": penalty["title"],
                "turnsLeft": penalty["duration"],
            })
            print(f"  {loser.getName()} on rangaistuksessa {penalty['duration']} vuoroa.")
