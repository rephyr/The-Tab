"""
Receipt formatters for the TaskGame drinking game.

formatTaskDraw  — single task card drawn during play
formatReceipt   — end-of-game summary (title, scores)

Printer API used in this module:

p.set(align, bold, double_width, double_height, invert)
p.textln(text) — prints one line
"""
from printing.receipts.textWrapper import wrapText as _wrapText

_W = 32


def configure(config: dict) -> None:
    global _W
    _W = int(config.get("receiptWidth", 32))


def formatTaskDraw(event, p) -> None:
    """Print a single TaskGame task receipt."""
    p.set(align="center", bold=True, double_width=True, double_height=True)
    p.textln(event.title.upper())
    p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("=" * _W)
    for line in _wrapText("Pelaajat: " + ", ".join(event.targets), _W):
        p.textln(line)
    for line in _wrapText(event.description, _W):
        p.textln(line)
    p.textln("=" * _W)


def formatChainDraw(event, p) -> None:
    """Print the chain card receipt with all player drink amounts and cascades."""
    p.set(align="center", bold=True, double_width=True, double_height=True)
    p.textln(event.title.upper())
    p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("=" * _W)
    for line in _wrapText(event.description, _W):
        p.textln(line)
    p.textln("-" * _W)
    for a in event.assignments:
        p.textln(f"{a['name']}: {a['amount']}")
        for c in a.get("cascades", []):
            p.textln(f"  +{c['name']}: {c['amount']} ({c['reason']})")
    p.textln("=" * _W)


def formatDrinkSummary(event, p) -> None:
    """Print a per-round drink summary — only players who drank this turn, with this turn's amounts."""
    if not event.scores:
        return
    p.set(align="center", bold=True)
    p.textln("JUOMAT")
    p.set(align="left", bold=False)
    p.textln("=" * _W)
    for s in event.scores:
        parts = []
        if s["drank"] > 0:
            parts.append(f"juo {s['drank']}")
        if s["toGive"] > 0:
            parts.append(f"antaa {s['toGive']}")
        p.textln(f"{s['name']}: {' | '.join(parts)}")
    p.textln("=" * _W)


def formatTally(scores: list, p) -> None:
    """Print the final drink tally."""
    p.set(align="center", bold=True)
    p.textln("LOPPUSALDO")
    p.set(align="left", bold=False)
    p.textln("=" * _W)
    for s in scores:
        p.textln(f"{s['name']}: joi {s['drank']} | antoi {s['gave']}")
    p.textln("=" * _W)


def formatReceipt(data: dict, p) -> None:
    """Print the end-of-game tally."""
    formatTally(data["scores"], p)
