"""
Receipt formatters for the TaskGame drinking game.

formatTaskDraw  — single task card drawn during play
formatReceipt   — end-of-game summary (title, scores)

Printer API used in this module:

p.set(align, bold, double_width, double_height, invert)
p.textln(text) — prints one line
"""

_W = 32

from printing.receipts.textWrapper import wrapText as _wrapText


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
    """Print a mid-game drink tally card after each turn."""
    active = [s for s in event.scores if s["drank"] > 0 or s["toGive"] > 0]
    if not active:
        return
    p.set(align="center", bold=True)
    p.textln("LASKURI")
    p.set(align="left", bold=False)
    p.textln("=" * _W)
    for s in active:
        p.textln(f"{s['name']}: joi {s['drank']} | antaa {s['toGive']}")
    p.textln("=" * _W)


def formatReceipt(data: dict, p) -> None:
    """Print the end-of-game summary: title, timestamp, players, and drink scores."""
    p.set(align="center", bold=True, double_width=True, double_height=True)
    p.textln("TASKGAME")
    p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("=" * _W)
    p.textln(data["timestamp"])
    p.textln(", ".join(data["players"]))
    p.textln("=" * _W)
    p.set(align="center", bold=True)
    p.textln("LOPPUSALDO")
    p.set(align="left", bold=False)
    p.textln("=" * _W)
    for score in data["scores"]:
        p.textln(f"{score['name']}: joi {score['drank']} | antoi {score['gave']}")
    p.textln("=" * _W)
