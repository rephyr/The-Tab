WIDTH = 32


def _line(char="-"):
    return char * WIDTH


def _center(text):
    return text.center(WIDTH)


def formatReceipt(data: dict) -> str:
    lines = []

    lines.append(_line("="))
    lines.append(_center("KUITTIPELI"))
    lines.append(_center("BUJA"))
    lines.append(_center(data["timestamp"]))
    lines.append(_line("="))
    lines.append("PLAYERS: " + ", ".join(data["players"]))

    if data["board"]:
        lines.append("")
        lines.append(_line("-"))
        lines.append("BOARD")
        lines.append(_line("-"))

        for card in data["board"]:
            lines.append(f"\n  {card['card']} [{card['action'].upper()}] {card['drinks']} drinks")
            if not card["matched"]:
                lines.append("    no match")
            else:
                for outcome in card["outcomes"]:
                    if outcome["type"] == "drink":
                        lines.append(f"    {outcome['player']} drinks {outcome['drinks']}")
                    elif outcome["type"] == "give":
                        lines.append(f"    {outcome['giver']} -> {outcome['receiver']} drinks {outcome['drinks']}")
                    elif outcome["type"] == "share":
                        lines.append(f"    {outcome['player1']} & {outcome['player2']} share {outcome['drinks']}")

    lines.append("")
    lines.append(_line("="))
    lines.append(_center("FINAL TALLY"))
    lines.append(_line("="))
    for score in data["scores"]:
        lines.append(f"{score['name']}: drank {score['drank']} | gave {score['gave']}")
    lines.append(_line("="))
    lines.append(_center("drink responsibly"))
    lines.append(_line("="))

    return "\n".join(lines) + "\n\n\n"
