"""Receipt formatters for the Mexico dice bluffing game."""
from printing.receipts.textWrapper import wrapText as _wrapText

_W = 32


def configure(config: dict) -> None:
    global _W
    _W = int(config.get("receiptWidth", 32))


def _displayClaimScore(score: int) -> str:
    if score == 1000:
        return "Mexico (2-1)"
    if score > 100:
        d = score - 200
        return f"Parit ({d}-{d})"
    high = score // 10
    low = score % 10
    return f"{score} ({high}-{low})"


def formatChallenge(event, p) -> None:
    """Print a receipt when a challenge is resolved and someone drinks."""
    p.set(align="center", bold=True)
    p.textln("MEXICO")
    p.set(align="left", bold=False)
    p.textln("=" * _W)

    if event.wasMexico:
        p.set(align="center", bold=True, double_width=True, double_height=True)
        p.textln("MEXICO!")
        p.set(align="left", bold=False, double_width=False, double_height=False)
        p.textln("-" * _W)

    for line in _wrapText(f"Väittäjä: {event.claimer}", _W):
        p.textln(line)
    for line in _wrapText(f"Haastaja: {event.challenger}", _W):
        p.textln(line)
    p.textln("-" * _W)
    for line in _wrapText(f"Väitti:  {_displayClaimScore(event.claimed)}", _W):
        p.textln(line)
    for line in _wrapText(f"Heitti:  {_displayClaimScore(event.actual)}", _W):
        p.textln(line)
    p.textln("-" * _W)

    if event.loser == event.claimer:
        verdict = f"{event.claimer} valehteli!".upper()
        p.set(align="center", bold=True, double_width=True, double_height=True, invert=True)
        p.textln(verdict)
        p.set(align="left", bold=False, double_width=False, double_height=False, invert=False)
    else:
        verdict = f"{event.challenger} haastoi turhaan!".upper()
        p.set(align="center", bold=True, double_width=True, double_height=True)
        p.textln(verdict)
        p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("")
    p.set(bold=True)
    for line in _wrapText(f"{event.loser} juo {event.drinks}!", _W):
        p.textln(line)
    p.set(bold=False)
    p.textln("=" * _W)


def formatAccept(event, p) -> None:
    """Print the current claim when a challenge is passed — shows what must be beaten next."""
    p.set(align="center", bold=True)
    p.textln("MEXICO")
    p.set(align="left", bold=False)
    p.textln("=" * _W)
    p.set(align="center", bold=True, double_width=True, double_height=True)
    p.textln(_displayClaimScore(event.claimed))
    p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("-" * _W)
    for line in _wrapText(f"{event.accepter} hyväksyi", _W):
        p.textln(line)
    p.textln("=" * _W)


def formatTally(scores: list, p) -> None:
    """Print the final drink tally."""
    p.set(align="center", bold=True)
    p.textln("MEXICO")
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
