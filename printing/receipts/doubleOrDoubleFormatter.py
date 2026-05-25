"""Receipt formatters for the Double or Double higher/lower streak card game."""
from printing.receipts.textWrapper import wrapText as _wrapText

_W = 32


def configure(config: dict) -> None:
    global _W
    _W = int(config.get("receiptWidth", 32))


def formatCardDraw(event, p) -> None:
    """Print a receipt for each card drawn streak progress or wrong guess."""
    p.set(align="center", bold=True)
    p.textln("DoD")
    p.set(align="left", bold=False)
    p.textln("=" * _W)
    for line in _wrapText(event.player, _W):
        p.textln(line)
    p.textln("-" * _W)
    for line in _wrapText(f"Nykyinen: {event.previousCard}", _W):
        p.textln(line)
    p.textln("-" * _W)

    if event.correct:
        p.set(align="center", bold=True, double_width=True, double_height=True)
        p.textln("OIKEIN!")
        p.set(align="left", bold=False, double_width=False, double_height=False)
        for line in _wrapText(f"Putki: {event.streak}  |  Panos: {event.pot}", _W):
            p.textln(line)
        if event.multiplier > 1:
            for line in _wrapText(f"Kerroin: x{event.multiplier}", _W):
                p.textln(line)
    else:
        drinks = event.pot * event.multiplier
        p.set(align="center", bold=True, double_width=True, double_height=True, invert=True)
        p.textln("VÄÄRIN!")
        p.set(align="left", bold=False, double_width=False, double_height=False, invert=False)
        p.set(bold=True)
        for line in _wrapText(f"{event.player} juo {drinks}!", _W):
            p.textln(line)
        if event.chainedPlayer:
            for line in _wrapText(f"KETJU: {event.chainedPlayer} juo {drinks}!", _W):
                p.textln(line)
        p.set(bold=False)

    p.textln("-" * _W)
    for line in _wrapText(f"Nostettu: {event.card}", _W):
        p.textln(line)
    p.textln("=" * _W)


def formatEqualCard(event, p) -> None:
    """Print a receipt when an equal card is drawn."""
    p.set(align="center", bold=True)
    p.textln("DoD")
    p.set(align="left", bold=False)
    p.textln("=" * _W)
    for line in _wrapText(event.player, _W):
        p.textln(line)
    p.textln("-" * _W)
    for line in _wrapText(f"Nykyinen: {event.previousCard}", _W):
        p.textln(line)
    p.textln("-" * _W)
    p.set(align="center", bold=True, double_width=True, double_height=True, invert=True)
    p.textln("TASAINEN!")
    p.set(align="left", bold=False, double_width=False, double_height=False, invert=False)
    p.set(bold=True)
    for line in _wrapText(f"{event.player} juo {event.total}!", _W):
        p.textln(line)
    if event.chainedPlayer:
        for line in _wrapText(f"KETJU: {event.chainedPlayer} juo {event.total}!", _W):
            p.textln(line)
    p.set(bold=False)
    p.textln("-" * _W)
    for line in _wrapText(f"Nostettu: {event.card}", _W):
        p.textln(line)
    p.textln("=" * _W)


def formatDoubleOrDouble(event, p) -> None:
    """Print a receipt for the Double or Double challenge."""
    p.set(align="center", bold=True)
    p.textln("DoD")
    p.set(align="left", bold=False)
    p.textln("=" * _W)
    p.set(align="center", bold=True)
    p.textln("DOUBLE OR DOUBLE")
    p.set(align="left", bold=False)
    p.textln("-" * _W)
    for line in _wrapText(event.player, _W):
        p.textln(line)
    for line in _wrapText(f"DOD kortti: {event.previousCard}", _W):
        p.textln(line)
    p.textln("-" * _W)

    if event.correct:
        p.set(align="center", bold=True, double_width=True, double_height=True)
        p.textln("OIKEIN!")
        p.set(align="left", bold=False, double_width=False, double_height=False)
        p.set(bold=True)
        if event.target:
            for line in _wrapText(f"{event.target} juo {event.amount}!", _W):
                p.textln(line)
            if event.chainedPlayer:
                for line in _wrapText(f"KETJU: {event.chainedPlayer} juo {event.amount}!", _W):
                    p.textln(line)
        else:
            for line in _wrapText(f"Jaat {event.amount} juomaa!", _W):
                p.textln(line)
        p.set(bold=False)
    else:
        p.set(align="center", bold=True, double_width=True, double_height=True, invert=True)
        p.textln("VÄÄRIN!")
        p.set(align="left", bold=False, double_width=False, double_height=False, invert=False)
        p.set(bold=True)
        for line in _wrapText(f"{event.player} juo {event.amount}!", _W):
            p.textln(line)
        if event.chainedPlayer:
            for line in _wrapText(f"KETJU: {event.chainedPlayer} juo {event.amount}!", _W):
                p.textln(line)
        p.set(bold=False)

    p.textln("-" * _W)
    for line in _wrapText(f"Haaste: {event.challengeCard}", _W):
        p.textln(line)
    p.textln("=" * _W)


def formatExit(event, p) -> None:
    """Print a receipt when a player exits the streak voluntarily."""
    p.set(align="center", bold=True)
    p.textln("DoD")
    p.set(align="left", bold=False)
    p.textln("=" * _W)
    for line in _wrapText(f"{event.player}", _W):
        p.textln(line)
    p.textln("-" * _W)
    for line in _wrapText(f"Putki:  {event.streak}", _W):
        p.textln(line)
    for line in _wrapText(f"Antaa:  {event.pot} juomaa", _W):
        p.textln(line)
    p.textln("-" * _W)
    p.set(align="center", bold=True)
    p.textln("LINKITETTY")
    p.set(align="left", bold=False)
    p.textln("=" * _W)


def formatLinkResolved(event, p) -> None:
    """Print a receipt when the link firs and the linked player drinks."""
    p.set(align="center", bold=True)
    p.textln("DoD")
    p.set(align="left", bold=False)
    p.textln("=" * _W)
    p.set(align="center", bold=True)
    p.textln("LINKITETTY!")
    p.set(align="left", bold=False)
    p.textln("-" * _W)
    for line in _wrapText(f"{event.triggerPlayer} joi {event.amount}", _W):
        p.textln(line)
    p.textln("-" * _W)
    p.set(bold=True)
    for line in _wrapText(f"{event.linkedPlayer} juo {event.amount}!", _W):
        p.textln(line)
    p.set(bold=False)
    p.textln("=" * _W)


def formatTally(scores: list, p) -> None:
    """Print the final drink tally."""
    p.set(align="center", bold=True)
    p.textln("DoD")
    p.set(align="left", bold=False)
    p.textln("=" * _W)
    p.set(align="center", bold=True)
    p.textln("LOPPUSALDO")
    p.set(align="left", bold=False)
    p.textln("-" * _W)
    for s in sorted(scores, key=lambda x: x["drank"], reverse=True):
        for line in _wrapText(f"{s['name']}: joi {s['drank']}", _W):
            p.textln(line)
    p.textln("=" * _W)
