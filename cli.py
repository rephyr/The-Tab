import importlib
import pkgutil
import games
from core.game import Game
from core.player import Player
from printing.log import GameLog
from printing.formatter import formatReceipt
from printing.printer import ReceiptPrinter
from config import Config


def listGames():
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


def runCli():
    gamesList = listGames()

    if not gamesList:
        print("No games found.")
        return

    print("Available games:\n")

    for i, gameClass in enumerate(gamesList):
        print(f"{i + 1}. {gameClass.gameTitle}")

    userInput = input("\nChoose a game: ").strip()

    gameClass = None

    if userInput.isdigit():
        index = int(userInput) - 1
        if 0 <= index < len(gamesList):
            gameClass = gamesList[index]

    if gameClass is None:
        for game in gamesList:
            if game.gameTitle.lower() == userInput.lower():
                gameClass = game
                break

    if gameClass is None:
        print("Invalid selection.")
        return

    players = []

    print("\nEnter players (press enter to start):")
    playerId = 1

    while True:
        name = input(f"Player {playerId} name: ").strip()
        if name == "":
            break
        players.append(Player(playerId, name))
        playerId += 1

    if not players:
        print("No players added.")
        return

    log = GameLog()
    game = gameClass(players=players, log=log)

    print(f"\nStarting {game.gameTitle}...\n")

    game.playRound()

    data = log.toDict()
    printerConfig = Config().data.get("printer", {})
    ReceiptPrinter(printerConfig).printReceipt(data, formatReceipt)