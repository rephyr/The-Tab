"""
Editable test data for previewing receipt formatting without playing a game.
Change the values here to see how different content looks when printed.
"""
from printing.formatter import formatTurn, formatHand, formatBoardCard, formatTally, formatTaskDraw
from printing.receipts.ravit import formatBettingSlip, formatHorseEvent, formatRavitFinal, formatTiebreakStart, formatTiebreakElimination, formatTiebreakWinner
from core.events import TaskDrawEvent, HorseEventFiredEvent, TiebreakStartEvent, TiebreakEliminationEvent, TiebreakWinnerEvent

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


TEST_HORSES_RAVIT = [
    {"id": 1, "name": "Ukko",     "speed": 4, "endurance": 5, "luck": 3, "odds": 1.3,
     "position": 20, "alive": True,  "tiredRoundsLeft": 0, "stumbleRoundsLeft": 0},
    {"id": 2, "name": "Tuulikki", "speed": 2, "endurance": 2, "luck": 1, "odds": 3.0,
     "position": 14, "alive": True,  "tiredRoundsLeft": 0, "stumbleRoundsLeft": 0},
    {"id": 3, "name": "Laukki",   "speed": 1, "endurance": 2, "luck": 1, "odds": 5.0,
     "position": 5,  "alive": False, "tiredRoundsLeft": 0, "stumbleRoundsLeft": 0},
]

TEST_BETS_RAVIT = [
    {"player": "Testi Tatti", "horseId": 1, "amount": 3},
    {"player": "Testi Matti", "horseId": 2, "amount": 2},
]

TEST_RAVIT_FINAL_POSITIONS = [
    {"horseId": 1, "horseName": "Ukko",     "position": 20, "place": 1, "alive": True},
    {"horseId": 2, "horseName": "Tuulikki", "position": 14, "place": 2, "alive": True},
    {"horseId": 3, "horseName": "Laukki",   "position": 5,  "place": 4, "alive": False},
]

TEST_RAVIT_SCORES = [
    {"name": "Testi Tatti", "drank": 0, "gave": 2},
    {"name": "Testi Matti", "drank": 2, "gave": 0},
]

TEST_HORSE_EVENT_RAVIT = HorseEventFiredEvent(
    roundNumber=4, horseId=3, horseName="Laukki",
    eventType="death", detail="Laukki kaatuu ja poistuu kilpailusta!",
)

TEST_TIEBREAK_START = TiebreakStartEvent(
    combatants=[
        {"id": 1, "name": "Ukko",   "odds": 1.5, "health": 28, "maxHealth": 28, "strength": 4},
        {"id": 4, "name": "Myrsky", "odds": 3.0, "health": 20, "maxHealth": 20, "strength": 2},
    ]
)

TEST_TIEBREAK_ELIMINATION = TiebreakEliminationEvent(
    loserName="Myrsky",
    remaining=["Ukko"],
    combatants=[
        {"name": "Ukko",   "health": 19, "maxHealth": 28, "strength": 4},
        {"name": "Myrsky", "health": 0,  "maxHealth": 20, "strength": 2},
    ],
)

TEST_TIEBREAK_WINNER = TiebreakWinnerEvent(winnerName="Ukko", health=19, maxHealth=28, strength=4)


def printTestReceipts(printer, parts=None) -> None:
    """Print test receipts for the given parts.

    parts: list containing any of "turns", "hands", "board", "tally".
    Pass None to print all.
    """
    if parts is None:
        parts = ["turns", "hands", "board", "tally", "tasks",
                 "ravit-betting", "ravit-event", "ravit-tiebreak", "ravit-final"]

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

    if "ravit-betting" in parts:
        printer.printWith(lambda p: formatBettingSlip(TEST_HORSES_RAVIT, TEST_BETS_RAVIT, p))

    if "ravit-event" in parts:
        printer.printWith(lambda p, e=TEST_HORSE_EVENT_RAVIT: formatHorseEvent(e, p))

    if "ravit-tiebreak" in parts:
        printer.printWith(lambda p, e=TEST_TIEBREAK_START: formatTiebreakStart(e, p))
        printer.printWith(lambda p, e=TEST_TIEBREAK_ELIMINATION: formatTiebreakElimination(e, p))
        printer.printWith(lambda p, e=TEST_TIEBREAK_WINNER: formatTiebreakWinner(e, p))

    if "ravit-final" in parts:
        ravitData = {
            "players": ["Testi Tatti", "Testi Matti"],
            "timestamp": "2026-05-21 22:00",
            "horses": TEST_HORSES_RAVIT,
            "bets": TEST_BETS_RAVIT,
            "finalPositions": TEST_RAVIT_FINAL_POSITIONS,
            "scores": TEST_RAVIT_SCORES,
        }
        printer.printWith(lambda p, d=ravitData: formatRavitFinal(d, p))
