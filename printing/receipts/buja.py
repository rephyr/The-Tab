def formatReceipt(data: dict, p) -> None:
    p.set(align="center", bold=True, double_width=True, double_height=True)
    p.textln("BUJA")
    p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("=" * 24)
    p.textln(data["timestamp"])
    p.textln(", ".join(data["players"]))
    p.textln("=" * 24)

    if data["board"]:
        p.set(align="center", bold=True)
        p.textln("BOARD")
        p.set(align="left", bold=False)
        p.textln("-" * 24)

        for card in data["board"]:
            p.set(align="center", bold=True, double_width=True, double_height=True, invert=bool(card["matched"]))
            p.textln(card["card"])
            p.set(align="left", bold=False, double_width=False, double_height=False, invert=False)
            p.textln(f"{card['action'].upper()} - {card['drinks']} drinks")

            if not card["matched"]:
                p.textln("No match")
            else:
                for outcome in card["outcomes"]:
                    if outcome["type"] == "drink":
                        p.textln(f"{outcome['player']} drinks {outcome['drinks']}")
                    elif outcome["type"] == "give":
                        p.textln(f"{outcome['giver']} -> {outcome['receiver']} drinks {outcome['drinks']}")
                    elif outcome["type"] == "share":
                        p.textln(f"{outcome['player1']} & {outcome['player2']} share {outcome['drinks']}")
            p.textln("-" * 24)

    p.set(align="center", bold=True)
    p.textln("FINAL TALLY")
    p.set(align="left", bold=False)
    p.textln("=" * 24)
    for score in data["scores"]:
        p.textln(f"{score['name']}: drank {score['drank']} | gave {score['gave']}")
    p.textln("=" * 24)
    p.set(align="center")
    p.textln("drink responsibly")
