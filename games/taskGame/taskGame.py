"""
TaskGame: a turn-based drinking game where each turn a random task is drawn.
Tasks can target a single player, multiple random players, or everyone.
"""
from core.game import Game
from core.events import GameStartEvent, GameEndEvent
from dataclasses import dataclass, field
from games.taskGame.tasks import TASKS
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

    def playRound(self) -> None:
        """Run a full game: players take turns drawing tasks until someone quits."""
        self.emit(GameStartEvent([p.getName() for p in self.players]))

        taskPool = list(TASKS)

        if not taskPool:
            print("No tasks defined.")
            return

        running = True
        while running:
            for player in self.players:
                self._showLinks()
                input(f"\n{player.getName()}'s turn -- press Enter to draw a task")

                if not taskPool:
                    taskPool = list(TASKS)

                task = random.choice(taskPool)

                targets = self._resolveTargets(task["players"], player)
                targetNames = ", ".join(p.getName() for p in targets)

                print(f"\n>>> {task['title']}")
                print(f"Players: {targetNames}")
                print(task["description"])

                self._handlePostTask(task, targets, player)

                quit = input("\nContinue? (Enter = yes, q = quit): ").strip().lower()
                if quit == "q":
                    running = False
                    break

        self.emit(GameEndEvent([
            {"name": p.getName(), "drinksTaken": p.getDrinksTaken(), "drinksToGive": p.drinksToGive}
            for p in self.players
        ]))

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

    def _assignDrinks(self, player, amount: int) -> None:
        """Add drinks to a player and propagate one hop through active links."""
        player.addDrinks(amount)
        for p1, p2 in self.activePairs:
            if player == p1:
                p2.addDrinks(amount)
                print(f"  {p2.getName()} also drinks {amount} (pari)")
            elif player == p2:
                p1.addDrinks(amount)
                print(f"  {p1.getName()} also drinks {amount} (pari)")
        for master, huora in self.activeHuoras:
            if player == master:
                huora.addDrinks(amount)
                print(f"  {huora.getName()} also drinks {amount} (huora)")

    def _findPlayer(self, name: str):
        """Return the player whose name matches (case-insensitive), or None."""
        for p in self.players:
            if p.getName().lower() == name.lower():
                return p
        return None

    def _showLinks(self) -> None:
        """Print active pair and huora links if any exist."""
        parts = []
        for p1, p2 in self.activePairs:
            parts.append(f"{p1.getName()} ↔ {p2.getName()} (pari)")
        for master, huora in self.activeHuoras:
            parts.append(f"{huora.getName()} → {master.getName()} (huora)")
        if parts:
            print("Active links: " + " | ".join(parts))

    def _handlePostTask(self, task: dict, targets: list, drawer) -> None:
        """Handle drink tracking and link updates after a task is shown."""
        drinkType = task.get("drinkType", "social")
        drinks = task.get("drinks")

        if drinkType == "take":
            raw = input(f"\nConfirm {drinks} drinks for {drawer.getName()}? (Enter = yes, or type amount): ").strip()
            amount = drinks
            if raw.isdigit():
                amount = int(raw)
            if amount > 0:
                self._assignDrinks(drawer, amount)

        elif drinkType == "give":
            names = ", ".join(p.getName() for p in self.players if p != drawer)
            raw = input(f"\nWho gets the {drinks} drinks? ({names}) or Enter to skip: ").strip()
            if raw:
                receiver = self._findPlayer(raw)
                if receiver and receiver != drawer:
                    self._assignDrinks(receiver, drinks)
                    drawer.addDrinksToGive(drinks)
                elif receiver == drawer:
                    print("Can't give to yourself.")
                else:
                    print(f"Player '{raw}' not found, skipping.")

        elif drinkType == "social":
            hint = f" (suggested: {drinks})" if drinks is not None else ""
            raw = input(f"\nLog drinks{hint} as Name:N pairs (e.g. Teppo:3 Matti:2) or Enter to skip: ").strip()
            if raw:
                for token in raw.split():
                    if ":" not in token:
                        continue
                    name, _, val = token.partition(":")
                    if not val.isdigit():
                        continue
                    player = self._findPlayer(name)
                    if player:
                        self._assignDrinks(player, int(val))
                    else:
                        print(f"  Player '{name}' not found, skipping.")

        elif drinkType == "link":
            if not targets:
                return
            target = targets[0]
            if task["title"] == "Pari":
                self.activePairs.clear()
                self.activePairs.append([drawer, target])
                print(f"\nNew pair: {drawer.getName()} ↔ {target.getName()} (replaces any previous pair)")
            elif task["title"] == "Huora":
                self.activeHuoras.append([drawer, target])
                print(f"\nNew huora: {target.getName()} drinks whenever {drawer.getName()} drinks")
