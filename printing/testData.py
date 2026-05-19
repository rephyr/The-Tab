"""
Editable test data for previewing receipt formatting without playing a game.
Change the values here to see how different content looks when printed.
"""
from printing.formatter import formatTurn, formatHand, formatBoardCard, formatTally, formatTaskDraw
from core.events import TaskDrawEvent

TEST_PHASES = [
    ("Red or Black", {
        "player": "Testi Tatti",
        "guess": "Red",
        "card": "♥7",
        "correct": True,
        "gaveTo": "Testi Matti",
        "drinks": 1,
        "note": None,
        "handBefore": [],
    }),
    ("Higher or Lower", {
        "player": "Testi Matti",
        "guess": "Higher",
        "card": "♠J",
        "correct": False,
        "gaveTo": None,
        "drinks": 2,
        "note": None,
        "handBefore": ["♥7"],
    }),
    ("Inside or Outside", {
        "player": "Testi Tatti",
        "guess": "Inside",
        "card": "♦8",
        "correct": True,
        "gaveTo": "Testi Matti",
        "drinks": 3,
        "note": None,
        "handBefore": ["♥7", "♠J"],
    }),
    ("Suit", {
        "player": "Testi Matti",
        "guess": "Hearts",
        "card": "♣K",
        "correct": False,
        "gaveTo": None,
        "drinks": 4,
        "note": None,
        "handBefore": [],
    }),
]

TEST_HANDS = [
    ("Testi Tatti", ["♥7", "♠J", "♦8", "♣K"]),
    ("Testi Matti", ["♥Q", "♣5", "♠A", "♦3"]),
]

TEST_BOARD_CARDS = [
    {
        "card": "♦Q",
        "action": "Drink",
        "drinks": 2,
        "matched": [],
        "outcomes": [],
    },
    {
        "card": "♠7",
        "action": "Drink",
        "drinks": 2,
        "matched": ["Testi Tatti"],
        "outcomes": [
            {"player": "Testi Tatti", "type": "drink", "drinks": 2},
        ],
    },
    {
        "card": "♥J",
        "action": "Give",
        "drinks": 4,
        "matched": ["Testi Tatti"],
        "outcomes": [
            {"giver": "Testi Tatti", "receiver": "Testi Matti", "type": "give", "drinks": 4},
        ],
    },
    {
        "card": "♣A",
        "action": "Share",
        "drinks": 6,
        "matched": ["Testi Tatti", "Testi Matti"],
        "outcomes": [
            {"player1": "Testi Tatti", "player2": "Testi Matti", "type": "share", "drinks": 6},
        ],
    },
]

TEST_SCORES = [
    {"name": "Testi Tatti", "drank": 8, "gave": 5},
    {"name": "Testi Matti", "drank": 12, "gave": 3},
]

TEST_TASK_DRAWS = [
    TaskDrawEvent(drawer="Testi Tatti", title="Juo 3",      description="Juo 3.",                                                                                              targets=["Testi Tatti"]),
    TaskDrawEvent(drawer="Testi Tatti", title="Jaa 3",      description="Jaa 3 juomaa.",                                                                                       targets=["Testi Tatti"]),
    TaskDrawEvent(drawer="Testi Tatti", title="Pari",       description="Teette parin. Aina kun toinen juo, toinen juo myös. Kestää kunnes seuraava parikortti nostetaan.",     targets=["Testi Tatti", "Testi Matti"]),
    TaskDrawEvent(drawer="Testi Tatti", title="Vesiputous", description="Kaikki alkavat juomaan yhtäikaa. Kukaan ei saa lopettaa ennen kuin oikealla puolella oleva lopettaa.", targets=["Testi Tatti", "Testi Matti"]),
]


def printTestReceipts(printer, parts=None) -> None:
    """Print test receipts for the given parts.

    parts: list containing any of "turns", "hands", "board", "tally".
    Pass None to print all.
    """
    if parts is None:
        parts = ["turns", "hands", "board", "tally", "tasks"]

    if "turns" in parts:
        for phaseName, turn in TEST_PHASES:
            printer.printWith(lambda p, ph=phaseName, t=turn: formatTurn(ph, t, p))

    if "hands" in parts:
        for playerName, cards in TEST_HANDS:
            printer.printWith(lambda p, pn=playerName, c=cards: formatHand(pn, c, p))

    if "board" in parts:
        for card in TEST_BOARD_CARDS:
            printer.printWith(lambda p, c=card: formatBoardCard(c, p))

    if "tally" in parts:
        printer.printWith(lambda p: formatTally(TEST_SCORES, p))

    if "tasks" in parts:
        for event in TEST_TASK_DRAWS:
            printer.printWith(lambda p, e=event: formatTaskDraw(e, p))
