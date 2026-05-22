"""
Receipt formatters for the Buja card drinking game.

formatTurn           — one player's turn in any phase
formatHand           — player's full card hand
formatBoardCard      — one board card with action and outcomes
formatTally          — end-of-game drink totals
formatRouletteResult — Russian roulette result card
formatReceipt        — full game receipt (all turns, hands, board, tally)
formatEndReceipt     — compact end-of-game summary (title, board, scores)

Printer API used in this module:

p.set(align, bold, double_width, double_height, invert)
p.textln(text) — prints one line
"""

_W = 32


def configure(config: dict) -> None:
    global _W
    _W = int(config.get("receiptWidth", 32))


def formatTurn(phaseName: str, turn: dict, p) -> None:
    """Print one player's turn receipt for a phase."""
    p.textln("=" * _W)
    p.set(align="center", bold=True)
    p.textln(phaseName.upper())
    p.set(align="left", bold=False)
    p.textln("-" * _W)
    p.textln(f"Pelaaja : {turn['player']}")
    if phaseName == "Välistä vai ulkoa?" and turn.get("handBefore"):
        hand = turn["handBefore"]
        p.textln("Kädessä:")
        p.set(align="center", bold=True, double_width=True, double_height=True)
        p.textln("  ".join(hand))
        p.set(align="left", bold=False, double_width=False, double_height=False)
    if turn["guess"]:
        p.textln(f"Arvaus  : {turn['guess']}")
    if turn["card"]:
        if phaseName == "Isompi vai pienempi?" and turn.get("handBefore"):
            display = f"{turn['handBefore'][-1]}  {turn['card']}"
        else:
            display = turn["card"]
        p.textln("")
        p.set(align="center", bold=True, double_width=True, double_height=True, invert=True)
        p.textln(display)
        p.set(align="left", bold=False, double_width=False, double_height=False, invert=False)
        p.textln("")
    if turn["gaveTo"]:
        p.textln(f"Oikein! {turn['gaveTo']} juo {turn['drinks']}.")
    elif turn.get("correct") is True:
        p.textln("Oikein!")
    elif turn["drinks"] > 0:
        note = f" ({turn['note']})" if turn["note"] else ""
        p.textln(f"Väärin! Juo {turn['drinks']}{note}.")
    currentHand = list(turn.get("handBefore") or [])
    if turn.get("card"):
        currentHand.append(turn["card"])
    if currentHand:
        p.textln("-" * _W)
        p.set(align="center", bold=True, double_width=True, double_height=True)
        p.textln("  ".join(currentHand))
        p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("-" * _W)


def formatHand(player: str, cards: list, p) -> None:
    """Print a player's full hand as a single receipt."""
    p.set(align="center", bold=True)
    p.textln(player.upper())
    p.set(align="left", bold=False)
    p.textln("=" * _W)
    p.set(align="center", bold=True, double_width=True, double_height=True)
    p.textln("  ".join(cards))
    p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("=" * _W)


def formatBoardCard(card: dict, p) -> None:
    """Print a board card receipt with its action and outcomes."""
    p.set(align="center", bold=True)
    p.textln("=" * _W)
    p.set(align="center", bold=True, double_width=True, double_height=True, invert=bool(card["matched"]))
    p.textln(card["card"])
    p.set(align="left", bold=False, invert=False)
    p.textln("-" * _W)
    p.set(align="left", bold=False, double_width=False, double_height=False, invert=False)
    p.textln(f"{card['action'].upper()} {card['drinks']}")
    if not card["matched"]:
        p.textln("Ei osumia")
    elif card["outcomes"]:
        for outcome in card["outcomes"]:
            if outcome["type"] == "drink":
                p.textln(f"{outcome['player']} juo {outcome['drinks']}")
            elif outcome["type"] == "give":
                p.textln(f"{outcome['giver']} -> {outcome['receiver']} juo {outcome['drinks']}")
            elif outcome["type"] == "share":
                p.textln(f"{outcome['player1']} & {outcome['player2']} kippistää {outcome['drinks']}")
    else:
        for name in card["matched"]:
            p.textln(name)
    p.set(align="left", bold=False, double_width=False, double_height=False, invert=False)
    p.set(align="center", bold=True)
    p.textln("=" * _W)


def formatTally(scores: list, p) -> None:
    """Print the final drink tally for all players."""
    p.set(align="center", bold=True)
    p.textln("LOPPUSALDO")
    p.set(align="left", bold=False)
    p.textln("=" * _W)
    for score in scores:
        p.textln(f"{score['name']}: joi {score['drank']} | antoi {score['gave']}")
    p.textln("=" * _W)


def formatRouletteResult(event, p) -> None:
    """Print a single player's roulette pull result."""
    p.set(align="center", bold=True)
    p.textln("VENÄLÄINEN RULETTI")
    p.set(align="left", bold=False)
    p.textln("=" * _W)
    p.set(align="center", bold=True, double_width=True, double_height=True)
    p.textln(event.player.upper())
    p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("=" * _W)
    if event.hit:
        p.set(align="center", bold=True, double_width=True, double_height=True, invert=True)
        p.textln("OSUMA!")
        p.set(align="left", bold=False, double_width=False, double_height=False, invert=False)
        p.textln(f"Juo {event.drinks}!")
    else:
        p.set(align="center", bold=True, double_width=True, double_height=True)
        p.textln("OHI!")
        p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("=" * _W)


def formatReceipt(data: dict, p) -> None:
    """Print the full game receipt: all turns, hands, board cards, and tally."""
    for phase in data["phases"]:
        for turn in phase["turns"]:
            formatTurn(phase["name"], turn, p)
            p.cut()
    for player, cards in data["hands"].items():
        formatHand(player, cards, p)
        p.cut()
    for card in data["board"]:
        formatBoardCard(card, p)
        p.cut()
    formatTally(data["scores"], p)


def formatEndReceipt(data: dict, p) -> None:
    """Print the compact end-of-game summary: title, board results, and drink scores."""
    p.set(align="center", bold=True, double_width=True, double_height=True)
    p.textln("BUJA")
    p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("=" * _W)
    p.textln(data["timestamp"])
    p.textln(", ".join(data["players"]))
    p.textln("=" * _W)

    if data["board"]:
        p.set(align="center", bold=True)
        p.textln("LAUTA")
        p.set(align="left", bold=False)
        p.textln("-" * _W)

        for card in data["board"]:
            p.set(align="center", bold=True, double_width=True, double_height=True, invert=bool(card["matched"]))
            p.textln(card["card"])
            p.set(align="left", bold=False, double_width=False, double_height=False, invert=False)
            p.textln(f"{card['action'].upper()} {card['drinks']}")

            if not card["matched"]:
                p.textln("Ei osumia")
            else:
                for outcome in card["outcomes"]:
                    if outcome["type"] == "drink":
                        p.textln(f"{outcome['player']} juo {outcome['drinks']}")
                    elif outcome["type"] == "give":
                        p.textln(f"{outcome['giver']} -> {outcome['receiver']} juo {outcome['drinks']}")
                    elif outcome["type"] == "share":
                        p.textln(f"{outcome['player1']} & {outcome['player2']} kippistää {outcome['drinks']}")
            p.textln("-" * _W)

    p.set(align="center", bold=True)
    p.textln("LOPPUSALDO")
    p.set(align="left", bold=False)
    p.textln("=" * _W)
    for score in data["scores"]:
        p.textln(f"{score['name']}: joi {score['drank']} | antoi {score['gave']}")
    p.textln("=" * _W)
