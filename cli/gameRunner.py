from core.player import Player
from core.playerStore import PlayerStore
from printing.log import GameLog
from printing.printer import ReceiptPrinter, NullPrinter
from printing.live import LivePrinter
from cli.utils import _clearScreen


def showSessionResult(scores: list[dict], title: str) -> None:
    if not scores:
        return
    _clearScreen()
    print(f"\n--- {title} — tulos ---\n")
    print(f"{'Nimi':<20} {'Joi':>6} {'Antoi':>6}")
    print("-" * 34)
    for s in sorted(scores, key=lambda x: x["drank"], reverse=True):
        print(f"{s['name']:<20} {s['drank']:>6} {s['gave']:>6}")
    print()
    input("Paina Enter jatkaaksesi...")


def configureGame(gameTitle: str, configData: dict) -> dict:
    defaults = configData.get(gameTitle.lower(), {})

    if not defaults:
        return {}

    _clearScreen()
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


def _checkDeckCount(gameClass: type, players: list[Player], gameConfig: dict) -> dict:
    if not hasattr(gameClass, "cardsNeeded"):
        return gameConfig

    boardLength = gameConfig.get("boardLength", 3)
    needed = gameClass.cardsNeeded(len(players), boardLength)
    while True:
        deckCount = gameConfig.get("deckCount", 1)
        available = 52 * deckCount
        if needed <= available:
            print(
                f"\nPakkakiintiö: tarvitaan {needed} korttia, "
                f"saatavilla {available} ({deckCount} pakka(a)). OK."
            )
            break
        recommended = -(-needed // 52)
        print(
            f"\nPakkakiintiö: tarvitaan {needed} korttia {len(players)} pelaajalle, "
            f"saatavilla vain {available} ({deckCount} pakka(a))."
        )
        print(f"Suositellaan: {recommended} pakka(a).")
        choice = input("Aseta pakkojen määrä tai paina Enter jatkaaksesi: ").strip()
        if not choice:
            break
        if choice.isdigit() and int(choice) > 0:
            gameConfig["deckCount"] = int(choice)
        else:
            print("Virheellinen numero.")

    return gameConfig


def runGame(
    gameClass: type,
    players: list[Player],
    gameConfig: dict,
    store: PlayerStore,
    receiptMode: bool,
    debug: bool,
    saveData: bool,
    printerConfig: dict,
) -> dict:
    gameConfig = _checkDeckCount(gameClass, players, gameConfig)

    printer = ReceiptPrinter(printerConfig, debug=debug) if receiptMode else NullPrinter()
    log = GameLog()
    store.gameTitle = gameClass.gameTitle
    log.on(LivePrinter(printer, gameTitle=gameClass.gameTitle).hook)
    if not debug and saveData:
        log.on(store.hook)

    game = gameClass(players=players, log=log, config=gameConfig)
    print(f"\nAloitetaan {game.gameTitle}...\n")
    game.playRound()

    return log.toDict()
