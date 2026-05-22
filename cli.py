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


def showSessionResult(scores, title):
    """Print the scores from a single just-completed game."""
    if not scores:
        return
    print(f"\n--- {title} — tulos ---\n")
    print(f"{'Nimi':<20} {'Joi':>6} {'Antoi':>6}")
    print("-" * 34)
    for s in sorted(scores, key=lambda x: x["drank"], reverse=True):
        print(f"{s['name']:<20} {s['drank']:>6} {s['gave']:>6}")
    print()
    input("Paina Enter jatkaaksesi...")


def showLeaderboard(store):
    """Print the all-time leaderboard ranked by drinks taken."""
    board = store.getLeaderboard()

    if not board:
        print("\nEi dataa vielä.\n")
        input("Paina Enter jatkaaksesi...")
        return

    print("\n--- Tulostaulukko ---\n")
    print(f"{'#':<4} {'Nimi':<20} {'Joi':>6} {'Antoi':>6} {'Pelit':>6}")
    print("-" * 46)
    for i, p in enumerate(board):
        print(f"{i + 1:<4} {p['name']:<20} {p['totalDrinksTaken']:>6} {p['totalDrinksGiven']:>6} {p['gamesPlayed']:>6}")

    print()
    input("Paina Enter jatkaaksesi...")


def _printSessionList(sessions):
    """Print a numbered list of sessions with players."""
    for i, s in enumerate(sessions):
        players = ", ".join(sc["name"] for sc in s["scores"])
        print(f"{i + 1}. [{s['timestamp']}] {s['game']} — {players}")


def showSession(store):
    """List sessions and display full details for a chosen one."""
    sessions = store.getSessions()
    if not sessions:
        print("\nEi sessioita tallennettu.")
        input("Paina Enter jatkaaksesi...")
        return

    print("\n--- Sessiot ---\n")
    _printSessionList(sessions)

    raw = input("\nKatsottavan session numero (tai Enter peruuttaaksesi): ").strip()
    if not raw:
        return
    if not raw.isdigit() or not (1 <= int(raw) <= len(sessions)):
        print("Virheellinen numero.")
        return

    s = sessions[int(raw) - 1]
    print(f"\n[{s['timestamp']}] {s['game']}\n")
    print(f"{'Nimi':<20} {'Joi':>6} {'Antoi':>6}")
    print("-" * 35)
    for sc in s["scores"]:
        print(f"{sc['name']:<20} {sc['drinksTaken']:>6} {sc['drinksGiven']:>6}")
    print()
    input("Paina Enter jatkaaksesi...")


def manageData(store):
    """Sub-menu for viewing, deleting players or sessions."""
    try:
        while True:
            print("\nHallitse dataa:")
            print("1. Katso sessiot")
            print("2. Poista pelaaja")
            print("3. Poista sessio")
            print("4. Takaisin")

            choice = input("\nValinta: ").strip()

            if choice == "1":
                showSession(store)

            elif choice == "2":
                names = store.getRegisteredPlayerNames()
                if not names:
                    print("Pelaajia ei löydy.")
                    continue
                print()
                for name in names:
                    print(f"  {name}")
                print()
                name = input("Poistettavan pelaajan nimi: ").strip()
                if not name:
                    continue
                confirm = input(f"Poista '{name}' ja kaikki tilastot? (k/e): ").strip().lower()
                if confirm != "k":
                    print("Peruutettu.")
                    continue
                if store.deletePlayer(name):
                    print(f"Pelaaja '{name}' poistettu.")
                else:
                    print(f"Pelaaja '{name}' löytyy vain sessiohistoriassa eikä sitä voi poistaa.")

            elif choice == "3":
                sessions = store.getSessions()
                if not sessions:
                    print("Ei sessioita poistettavaksi.")
                    continue

                print()
                _printSessionList(sessions)

                raw = input("\nPoistettavan session numero (tai Enter peruuttaaksesi): ").strip()
                if not raw:
                    continue
                if not raw.isdigit() or not (1 <= int(raw) <= len(sessions)):
                    print("Virheellinen numero.")
                    continue
                index = int(raw) - 1
                s = sessions[index]
                players = ", ".join(sc["name"] for sc in s["scores"])
                confirm = input(f"Poista sessio [{s['timestamp']}] {s['game']} — {players}? (k/e): ").strip().lower()
                if confirm != "k":
                    print("Peruutettu.")
                    continue
                if store.deleteSession(index):
                    print("Sessio poistettu.")
                else:
                    print("Virheellinen numero.")

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

    print(f"\nPeliasetukset ({gameTitle}):")
    for key, value in defaults.items():
        print(f"  {key} = {value}")

    overrides = dict(defaults)

    while True:
        key = input("\nMuuta asetus? (kirjoita nimi tai paina Enter ohittaaksesi): ").strip()
        if not key:
            break
        if key not in defaults:
            print(f"Tuntematon asetus '{key}'.")
            continue
        raw = input(f"Uusi arvo asetukselle {key}: ").strip()
        try:
            overrides[key] = type(defaults[key])(raw)
        except (ValueError, TypeError):
            print("Virheellinen arvo, pidetään alkuperäinen.")

    return overrides


def selectPlayers(store):
    """Enter players for a game, with numbered quick-select from PlayerStore history."""
    savedNames = store.getAllPlayerNames()
    players = []
    existingNames = set()

    print("\nSyötä pelaajat:")
    if savedNames:
        print()
        for i, name in enumerate(savedNames, 1):
            print(f"  {i}. {name}")
    print()

    playerId = 1
    while True:
        raw = input(f"Pelaaja {playerId} (numero tai nimi, Enter lopettaa): ").strip()
        if raw == "":
            break
        if raw.isdigit() and 1 <= int(raw) <= len(savedNames):
            name = savedNames[int(raw) - 1]
        else:
            name = raw.title()
        uniqueName = deduplicateName(name, existingNames)
        if uniqueName != name:
            print(f"  Nimi on jo käytössä, käytetään '{uniqueName}'")
        existingNames.add(uniqueName)
        players.append(Player(playerId, uniqueName))
        playerId += 1

    return players


def deduplicateName(name, existingNames):
    """Return a unique version of name by appending (2), (3), etc. if needed."""
    if name not in existingNames:
        return name
    counter = 2
    while f"{name} ({counter})" in existingNames:
        counter += 1
    return f"{name} ({counter})"


def showPrintTest(config, debug):
    """Two-level sub-menu: choose game, then choose which part to print."""
    from printing.testData import printTestReceipts, GAMES
    printerConfig = config.data.get("printer", {})
    printer = ReceiptPrinter(printerConfig, debug=debug)
    gameNames = list(GAMES.keys())

    try:
        while True:
            print("\nTulosta testikuitit — valitse peli:")
            for i, name in enumerate(gameNames, 1):
                print(f"{i}. {name}")
            print(f"{len(gameNames)+1}. Kaikki")
            print(f"{len(gameNames)+2}. Takaisin")

            choice = input("\nValinta: ").strip()

            if choice == str(len(gameNames)+2):
                break
            elif choice == str(len(gameNames)+1):
                printTestReceipts(printer, None)
            elif choice.isdigit() and 1 <= int(choice) <= len(gameNames):
                gameName = gameNames[int(choice)-1]
                gameParts = GAMES[gameName]

                while True:
                    print(f"\n{gameName} — valitse osio:")
                    for i, (_, label) in enumerate(gameParts, 1):
                        print(f"{i}. {label}")
                    print(f"{len(gameParts)+1}. Kaikki {gameName}")
                    print(f"{len(gameParts)+2}. Takaisin")

                    partChoice = input("\nValinta: ").strip()

                    if partChoice == str(len(gameParts)+2):
                        break
                    elif partChoice == str(len(gameParts)+1):
                        printTestReceipts(printer, [k for k, _ in gameParts])
                    elif partChoice.isdigit() and 1 <= int(partChoice) <= len(gameParts):
                        key = gameParts[int(partChoice)-1][0]
                        printTestReceipts(printer, [key])
                    else:
                        print("Virheellinen valinta.")
            else:
                print("Virheellinen valinta.")
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
        print("Pelejä ei löydy.")
        return

    config = Config()
    store = PlayerStore()
    receiptMode = True
    saveData = True

    modeLabel = " [ADMIN]" if adminMode else ""
    if debug:
        modeLabel += " [DEBUG]"
    try:
        while True:
            receiptLabel = "PÄÄLLÄ" if receiptMode else "POIS"
            saveLabel = "PÄÄLLÄ" if saveData else "POIS"
            print(f"\nPelit{modeLabel}:\n")
            for i, gameClass in enumerate(gamesList):
                print(f"{i + 1}. {gameClass.gameTitle}")
            print("\nL - Tulostaulukko")
            print("S - Sessiot")
            if adminMode:
                print("M - Hallitse dataa")
            if debug:
                print("P - Testi tulostus")
            print(f"T - Tulostustila: kuitit [{receiptLabel}]")
            print(f"D - Tallenna pelin tiedot [{saveLabel}]")
            print('\n(kirjoita "quit" poistuaksesi)')

            userInput = input("\nValinta: ").strip()

            if userInput.lower() == "quit":
                break

            if userInput.lower() == "l":
                showLeaderboard(store)
                continue

            if userInput.lower() == "s":
                showSession(store)
                continue

            if userInput.lower() == "m" and adminMode:
                manageData(store)
                continue

            if userInput.lower() == "p" and debug:
                showPrintTest(config, debug)
                continue

            if userInput.lower() == "t":
                receiptMode = not receiptMode
                print(f"Tulostustila: kuitit {'PÄÄLLÄ' if receiptMode else 'POIS'}")
                continue

            if userInput.lower() == "d":
                saveData = not saveData
                print(f"Tallenna pelin tiedot: {'PÄÄLLÄ' if saveData else 'POIS'}")
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
                print("Virheellinen valinta.")
                continue

            players = selectPlayers(store)

            if not players:
                print("Ei pelaajia lisätty.")
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
                        print(f"\nPakkakiintiö: tarvitaan {needed} korttia, saatavilla {available} ({deckCount} pakka(a)). OK.")
                        break
                    recommended = -(-needed // 52)
                    print(f"\nPakkakiintiö: tarvitaan {needed} korttia {len(players)} pelaajalle, "
                          f"saatavilla vain {available} ({deckCount} pakka(a)).")
                    print(f"Suositellaan: {recommended} pakka(a).")
                    choice = input("Aseta pakkojen määrä tai paina Enter jatkaaksesi: ").strip()
                    if not choice:
                        break
                    if choice.isdigit() and int(choice) > 0:
                        gameConfig["deckCount"] = int(choice)
                    else:
                        print("Virheellinen numero.")

            printerConfig = config.data.get("printer", {})
            from printing.printer import NullPrinter
            printer = ReceiptPrinter(printerConfig, debug=debug) if receiptMode else NullPrinter()
            log = GameLog()
            store.gameTitle = gameClass.gameTitle
            log.on(LivePrinter(printer, gameTitle=gameClass.gameTitle).hook)
            if not debug and saveData:
                log.on(store.hook)
            game = gameClass(players=players, log=log, config=gameConfig)

            print(f"\nAloitetaan {game.gameTitle}...\n")

            game.playRound()

            result = log.toDict()
            showSessionResult(result["scores"], game.gameTitle)
    except KeyboardInterrupt:
        print()
