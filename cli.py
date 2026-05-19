import importlib
import pkgutil
import games
from core.game import Game
from core.player import Player
from core.playerStore import PlayerStore
from printing.log import GameLog
from printing.printer import ReceiptPrinter
from printing.live import LivePrinter
from config import Config


def listGames():
    """Discover all Game subclasses with a gameTitle in the games package."""
    gameClasses = []

    def walk(package):
        for moduleInfo in pkgutil.iter_modules(package.__path__):
            moduleName = moduleInfo.name
            fullName = package.__name__ + "." + moduleName
            module = importlib.import_module(fullName)

            if hasattr(module, "__path__"):
                walk(module)
                continue

            for itemName in dir(module):
                item = getattr(module, itemName)

                if (
                    isinstance(item, type)
                    and issubclass(item, Game)
                    and item is not Game
                    and hasattr(item, "gameTitle")
                    and item.gameTitle
                ):
                    gameClasses.append(item)

    walk(games)
    return gameClasses


def showLeaderboard(store):
    """Print the all-time leaderboard ranked by drinks taken."""
    board = store.getLeaderboard()

    if not board:
        print("\nNo data yet.\n")
        input("Press Enter to continue...")
        return

    print("\n--- Leaderboard ---\n")
    print(f"{'#':<4} {'Name':<20} {'Taken':>6} {'Given':>6} {'Games':>6}")
    print("-" * 46)
    for i, p in enumerate(board):
        print(f"{i + 1:<4} {p['name']:<20} {p['totalDrinksTaken']:>6} {p['totalDrinksGiven']:>6} {p['gamesPlayed']:>6}")

    print()
    input("Press Enter to continue...")


def _printSessionList(sessions):
    """Print a numbered list of sessions with players."""
    for i, s in enumerate(sessions):
        players = ", ".join(sc["name"] for sc in s["scores"])
        print(f"{i + 1}. [{s['timestamp']}] {s['game']} — {players}")


def showSession(store):
    """List sessions and display full details for a chosen one."""
    sessions = store.getSessions()
    if not sessions:
        print("\nNo sessions recorded yet.")
        input("Press Enter to continue...")
        return

    print("\n--- Sessions ---\n")
    _printSessionList(sessions)

    raw = input("\nSession number to view (or Enter to cancel): ").strip()
    if not raw:
        return
    if not raw.isdigit() or not (1 <= int(raw) <= len(sessions)):
        print("Invalid number.")
        return

    s = sessions[int(raw) - 1]
    print(f"\n[{s['timestamp']}] {s['game']}\n")
    print(f"{'Name':<20} {'Taken':>6} {'Given':>6}")
    print("-" * 35)
    for sc in s["scores"]:
        print(f"{sc['name']:<20} {sc['drinksTaken']:>6} {sc['drinksGiven']:>6}")
    print()
    input("Press Enter to continue...")


def manageData(store):
    """Sub-menu for viewing, deleting players or sessions."""
    try:
        while True:
            print("\nManage data:")
            print("1. View sessions")
            print("2. Delete a player")
            print("3. Delete a session")
            print("4. Back")

            choice = input("\nChoice: ").strip()

            if choice == "1":
                showSession(store)

            elif choice == "2":
                names = store.getAllPlayerNames()
                if not names:
                    print("No players found.")
                    continue
                print()
                for name in names:
                    print(f"  {name}")
                print()
                name = input("Player name to delete: ").strip()
                if not name:
                    continue
                confirm = input(f"Delete '{name}' and all their stats? (y/n): ").strip().lower()
                if confirm != "y":
                    print("Cancelled.")
                    continue
                if store.deletePlayer(name):
                    print(f"Deleted player '{name}'.")
                else:
                    print(f"Player '{name}' only exists in session history and cannot be deleted.")

            elif choice == "3":
                sessions = store.getSessions()
                if not sessions:
                    print("No sessions to delete.")
                    continue

                print()
                _printSessionList(sessions)

                raw = input("\nSession number to delete (or Enter to cancel): ").strip()
                if not raw:
                    continue
                if not raw.isdigit() or not (1 <= int(raw) <= len(sessions)):
                    print("Invalid number.")
                    continue
                index = int(raw) - 1
                s = sessions[index]
                players = ", ".join(sc["name"] for sc in s["scores"])
                confirm = input(f"Delete session [{s['timestamp']}] {s['game']} — {players}? (y/n): ").strip().lower()
                if confirm != "y":
                    print("Cancelled.")
                    continue
                if store.deleteSession(index):
                    print("Session deleted.")
                else:
                    print("Invalid number.")

            elif choice == "4":
                break
    except KeyboardInterrupt:
        print()


def configureGame(gameTitle, configData):
    """Show current game settings and let the user override values for this session.

    Returns a dict of overrides (may be empty). Does not write to config.json.
    """
    defaults = configData.get(gameTitle.lower(), {})

    if not defaults:
        return {}

    print(f"\nGame settings ({gameTitle}):")
    for key, value in defaults.items():
        print(f"  {key} = {value}")

    overrides = dict(defaults)

    while True:
        key = input("\nChange a setting? (enter name or press Enter to skip): ").strip()
        if not key:
            break
        if key not in defaults:
            print(f"Unknown setting '{key}'.")
            continue
        raw = input(f"New value for {key}: ").strip()
        try:
            overrides[key] = type(defaults[key])(raw)
        except (ValueError, TypeError):
            print("Invalid value, keeping original.")

    return overrides


def deduplicateName(name, existingNames):
    """Return a unique version of name by appending (2), (3), etc. if needed."""
    if name not in existingNames:
        return name
    counter = 2
    while f"{name} ({counter})" in existingNames:
        counter += 1
    return f"{name} ({counter})"


def showPrintTest(config, debug):
    """Sub-menu for printing test receipts with constant data to preview formatting."""
    from printing.testData import printTestReceipts
    printerConfig = config.data.get("printer", {})
    printer = ReceiptPrinter(printerConfig, debug=debug)

    options = [
        ("1", "Turn receipts (all 4 phases)", ["turns"]),
        ("2", "Player hands",                 ["hands"]),
        ("3", "Board cards",                  ["board"]),
        ("4", "Final tally",                  ["tally"]),
        ("5", "TaskGame receipts",            ["tasks"]),
        ("6", "All of the above",             None),
    ]

    optionMap = {key: parts for key, _, parts in options}

    try:
        while True:
            print("\nPrint test receipts:")
            for key, label, _ in options:
                print(f"{key}. {label}")
            print("7. Back")

            choice = input("\nChoice: ").strip()

            if choice == "7":
                break
            elif choice in optionMap:
                printTestReceipts(printer, optionMap[choice])
            else:
                print("Invalid choice.")
    except KeyboardInterrupt:
        print()
    finally:
        printer.close()


def runCli(adminMode=False, debug=False):
    """Main CLI loop. Shows a menu, runs games, and handles data management.

    adminMode enables the manage data option for deleting players and sessions.
    """
    gamesList = listGames()

    if not gamesList:
        print("No games found.")
        return

    config = Config()
    store = PlayerStore()

    modeLabel = " [ADMIN]" if adminMode else ""
    if debug:
        modeLabel += " [DEBUG]"
    try:
        while True:
            print(f"\nAvailable games{modeLabel}:\n")
            for i, gameClass in enumerate(gamesList):
                print(f"{i + 1}. {gameClass.gameTitle}")
            print("\nL - Leaderboard")
            if adminMode:
                print("M - Manage data")
            if debug:
                print("P - Print test")
            print('\n(type "quit" to exit)')

            userInput = input("\nChoose: ").strip()

            if userInput.lower() == "quit":
                break

            if userInput.lower() == "l":
                showLeaderboard(store)
                continue

            if userInput.lower() == "m" and adminMode:
                manageData(store)
                continue

            if userInput.lower() == "p" and debug:
                showPrintTest(config, debug)
                continue

            gameClass = None

            if userInput.isdigit():
                index = int(userInput) - 1
                if 0 <= index < len(gamesList):
                    gameClass = gamesList[index]

            if gameClass is None:
                for g in gamesList:
                    if g.gameTitle.lower() == userInput.lower():
                        gameClass = g
                        break

            if gameClass is None:
                print("Invalid selection.")
                continue

            players = []
            existingNames = set()

            print("\nEnter players (press Enter to start):")
            playerId = 1

            while True:
                name = input(f"Player {playerId} name: ").strip()
                if name == "":
                    break
                uniqueName = deduplicateName(name, existingNames)
                if uniqueName != name:
                    print(f"  Name already taken, using '{uniqueName}'")
                existingNames.add(uniqueName)
                players.append(Player(playerId, uniqueName))
                playerId += 1

            if not players:
                print("No players added.")
                continue

            gameConfig = configureGame(gameClass.gameTitle, config.data)
            gameConfig["debug"] = debug

            if hasattr(gameClass, "cardsNeeded"):
                boardLength = gameConfig.get("boardLength", 3)
                needed = gameClass.cardsNeeded(len(players), boardLength)
                while True:
                    deckCount = gameConfig.get("deckCount", 1)
                    available = 52 * deckCount
                    if needed <= available:
                        print(f"\nDeck check: {needed} cards needed, {available} available ({deckCount} deck(s)). OK.")
                        break
                    recommended = -(-needed // 52)
                    print(f"\nDeck check: {needed} cards needed for {len(players)} players, "
                          f"but only {available} available ({deckCount} deck(s)).")
                    print(f"Recommended: {recommended} deck(s).")
                    choice = input("Set number of decks or press Enter to proceed anyway: ").strip()
                    if not choice:
                        break
                    if choice.isdigit() and int(choice) > 0:
                        gameConfig["deckCount"] = int(choice)
                    else:
                        print("Invalid number.")

            printerConfig = config.data.get("printer", {})
            log = GameLog()
            store.gameTitle = gameClass.gameTitle
            log.on(LivePrinter(ReceiptPrinter(printerConfig, debug=debug)).hook)
            log.on(store.hook)
            game = gameClass(players=players, log=log, config=gameConfig)

            print(f"\nStarting {game.gameTitle}...\n")

            game.playRound()

            showLeaderboard(store)
    except KeyboardInterrupt:
        print()
