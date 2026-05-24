import importlib
import pkgutil
import games
from core.game import Game
from core.playerStore import PlayerStore
from config import Config
from cli.utils import _clearScreen
from cli.players import selectPlayers
from cli.sessions import showLeaderboard, showDailyLeaderboard, showSession
from cli.dataManager import manageData
from cli.gameRunner import configureGame, runGame, showSessionResult
from cli.printTest import showPrintTest
from cli.rules import showRules


def listGames() -> list[type]:
    gameClasses: list[type] = []

    def walk(package) -> None:
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


def runCli(adminMode: bool = False, debug: bool = False) -> None:
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
            _clearScreen()
            receiptLabel = "PÄÄLLÄ" if receiptMode else "POIS"
            saveLabel = "PÄÄLLÄ" if saveData else "POIS"
            print(f"\nPelit{modeLabel}:\n")
            for i, gameClass in enumerate(gamesList):
                print(f"{i + 1}. {gameClass.gameTitle}")
            print("\nR - Säännöt")
            print("L - Tulostaulukko")
            print("P - Päivän tulostaulukko" if not debug else "P - Testi tulostus")
            print("S - Sessiot")
            if adminMode:
                print("M - Hallitse dataa")
            print(f"T - Tulostustila: kuitit [{receiptLabel}]")
            print(f"D - Tallenna pelin tiedot [{saveLabel}]")
            print('\n(kirjoita "quit" poistuaksesi)')

            userInput = input("\nValinta: ").strip()

            if userInput.lower() == "quit":
                break
            if userInput.lower() == "r":
                showRules()
                continue
            if userInput.lower() == "l":
                showLeaderboard(store)
                continue
            if userInput.lower() == "s":
                showSession(store)
                continue
            if userInput.lower() == "m" and adminMode:
                manageData(store)
                continue
            if userInput.lower() == "p" and not debug:
                showDailyLeaderboard(store)
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

            printerConfig = config.data.get("printer", {})
            result = runGame(gameClass, players, gameConfig, store, receiptMode, debug, saveData, printerConfig)
            showSessionResult(result["scores"], gameClass.gameTitle)

    except KeyboardInterrupt:
        print()
