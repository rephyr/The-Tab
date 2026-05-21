"""
Receipt formatters for the TaskGame drinking game.

formatTaskDraw  — single task card drawn during play
formatReceipt   — end-of-game summary (title, scores)

Printer API used in this module:

p.set(align, bold, double_width, double_height, invert)
p.textln(text) — prints one line
"""

# Adjust to match how many characters fit across your printer in normal font.
_W = 32


def _wrapText(text: str, width: int = _W) -> list:
    words = text.split()
    lines = []
    current = ""
    for word in words:
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= width:
            current += " " + word
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def formatTaskDraw(event, p) -> None:
    """Print a single TaskGame task receipt."""
    p.set(align="center", bold=True, double_width=True, double_height=True)
    p.textln(event.title.upper())
    p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("=" * _W)
    for line in _wrapText("Pelaajat: " + ", ".join(event.targets)):
        p.textln(line)
    for line in _wrapText(event.description):
        p.textln(line)
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
