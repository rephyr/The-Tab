from config import Config
from printing.printer import ReceiptPrinter
from cli.utils import _clearScreen


def showPrintTest(config: Config, debug: bool) -> None:
    from printing.testData import printTestReceipts, GAMES
    printerConfig = config.data.get("printer", {})
    printer = ReceiptPrinter(printerConfig, debug=debug)
    gameNames = list(GAMES.keys())

    try:
        while True:
            _clearScreen()
            print("\nTulosta testikuitit — valitse peli:")
            for i, name in enumerate(gameNames, 1):
                print(f"{i}. {name}")
            print(f"{len(gameNames) + 1}. Kaikki")
            print(f"{len(gameNames) + 2}. Takaisin")

            choice = input("\nValinta: ").strip()

            if choice == str(len(gameNames) + 2):
                break
            elif choice == str(len(gameNames) + 1):
                printTestReceipts(printer, None)
                input("\nTulostettu. Paina Enter jatkaaksesi...")
            elif choice.isdigit() and 1 <= int(choice) <= len(gameNames):
                gameName = gameNames[int(choice) - 1]
                gameParts = GAMES[gameName]

                while True:
                    _clearScreen()
                    print(f"\n{gameName} — valitse osio:")
                    for i, (_, label) in enumerate(gameParts, 1):
                        print(f"{i}. {label}")
                    print(f"{len(gameParts) + 1}. Kaikki {gameName}")
                    print(f"{len(gameParts) + 2}. Takaisin")

                    partChoice = input("\nValinta: ").strip()

                    if partChoice == str(len(gameParts) + 2):
                        break
                    elif partChoice == str(len(gameParts) + 1):
                        printTestReceipts(printer, [k for k, _ in gameParts])
                        input("\nTulostettu. Paina Enter jatkaaksesi...")
                    elif partChoice.isdigit() and 1 <= int(partChoice) <= len(gameParts):
                        key = gameParts[int(partChoice) - 1][0]
                        printTestReceipts(printer, [key])
                        input("\nTulostettu. Paina Enter jatkaaksesi...")
                    else:
                        print("Virheellinen valinta.")
            else:
                print("Virheellinen valinta.")
    except KeyboardInterrupt:
        print()
    finally:
        printer.close()
