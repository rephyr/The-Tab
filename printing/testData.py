"""
Editable test data for previewing receipt formatting without playing a game.
Change the values here to see how different content looks when printed.
"""
from printing.receipts.bujaFormatter import formatTurn, formatHand, formatBoardCard, formatTally
from printing.receipts.taskGameFormatter import formatTaskDraw
from printing.receipts.diceFormatter import formatChallenge as formatMexicoChallenge, formatTally as formatMexicoTally
from printing.receipts.ravitFormatter import (
    formatHorseList, formatJockeyList, formatBettingReceipt,
    formatRaceEvents, formatRaceTrack, formatHorseEvent, formatRavitWinner, formatRavitFinal,
    formatTiebreakStart, formatTiebreakElimination, formatTiebreakWinner,
    formatBettorDrink,
)
from core.events import (
    TaskDrawEvent, HorseEventFiredEvent,
    RaceRoundEvent, TiebreakStartEvent, TiebreakEliminationEvent, TiebreakWinnerEvent,
    RavitBettorDrinkEvent,
)
from games.diceGame.diceEvents import MexicanChallengeEvent

# ---------------------------------------------------------------------------
# Buja
# ---------------------------------------------------------------------------

TEST_PHASES = [
    ("Red or Black", {
        "player": "Testi Tatti", "guess": "Red", "card": "❤︎⁠7", "correct": True,
        "gaveTo": "Testi Matti", "drinks": 1, "note": None, "handBefore": [],
    }),
    ("Higher or Lower", {
        "player": "Testi Matti", "guess": "Higher", "card": "♠J", "correct": False,
        "gaveTo": None, "drinks": 2, "note": None, "handBefore": ["❤︎⁠7"],
    }),
    ("Inside or Outside", {
        "player": "Testi Tatti", "guess": "Inside", "card": "♦8", "correct": True,
        "gaveTo": "Testi Matti", "drinks": 3, "note": None, "handBefore": ["❤︎⁠7", "♠J"],
    }),
    ("Suit", {
        "player": "Testi Matti", "guess": "Hearts", "card": "♣K", "correct": False,
        "gaveTo": None, "drinks": 4, "note": None, "handBefore": [],
    }),
]

TEST_HANDS = [
    ("Testi Tatti", ["❤︎⁠7", "♠J", "♦8", "♣K"]),
    ("Testi Matti", ["❤︎⁠Q", "♣5", "♠A", "♦3"]),
]

TEST_BOARD_CARDS = [
    {"card": "♦Q", "action": "Drink", "drinks": 2, "matched": [], "outcomes": []},
    {"card": "♠7", "action": "Drink", "drinks": 2, "matched": ["Testi Tatti"],
     "outcomes": [{"player": "Testi Tatti", "type": "drink", "drinks": 2}]},
    {"card": "❤︎⁠J", "action": "Give", "drinks": 4, "matched": ["Testi Tatti"],
     "outcomes": [{"giver": "Testi Tatti", "receiver": "Testi Matti", "type": "give", "drinks": 4}]},
    {"card": "♣A", "action": "Share", "drinks": 6, "matched": ["Testi Tatti", "Testi Matti"],
     "outcomes": [{"player1": "Testi Tatti", "player2": "Testi Matti", "type": "share", "drinks": 6}]},
]

TEST_SCORES = [
    {"name": "Testi Tatti", "drank": 8, "gave": 5},
    {"name": "Testi Matti", "drank": 12, "gave": 3},
]

# ---------------------------------------------------------------------------
# TaskGame
# ---------------------------------------------------------------------------

TEST_TASK_DRAWS = [
    TaskDrawEvent(drawer="Testi Tatti", title="Juo 3",      description="Juo 3.",                                                                                              targets=["Testi Tatti"]),
    TaskDrawEvent(drawer="Testi Tatti", title="Jaa 3",      description="Jaa 3 juomaa.",                                                                                       targets=["Testi Tatti"]),
    TaskDrawEvent(drawer="Testi Tatti", title="Pari",       description="Teette parin. Aina kun toinen juo, toinen juo myös. Kestää kunnes seuraava parikortti nostetaan.",     targets=["Testi Tatti", "Testi Matti"]),
    TaskDrawEvent(drawer="Testi Tatti", title="Vesiputous", description="Kaikki alkavat juomaan yhtäaikaa. Kukaan ei saa lopettaa ennen kuin oikealla puolella oleva lopettaa.", targets=["Testi Tatti", "Testi Matti"]),
]

# ---------------------------------------------------------------------------
# Ravit
# ---------------------------------------------------------------------------

TEST_HORSES_RAVIT = [
    {"id": 1, "name": "Ukko",     "speed": 4, "endurance": 5, "luck": 3, "odds": 1.3,
     "position": 20, "status": "racing", "tiredRoundsLeft": 0, "stumbleRoundsLeft": 0},
    {"id": 2, "name": "Tuulikki", "speed": 2, "endurance": 2, "luck": 1, "odds": 3.0,
     "position": 14, "status": "racing", "tiredRoundsLeft": 0, "stumbleRoundsLeft": 0},
    {"id": 3, "name": "Laukki",   "speed": 1, "endurance": 2, "luck": 1, "odds": 5.0,
     "position": 5,  "status": "dead",   "tiredRoundsLeft": 0, "stumbleRoundsLeft": 0},
]

TEST_BETS_RAVIT = [
    {"player": "Testi Tatti", "horseId": 1, "amount": 3},
    {"player": "Testi Matti", "horseId": 2, "amount": 2},
]
TEST_JOCKEYS_RAVIT = [
    {"horseName": "Ukko",     "jockeyName": "Turbo",   "jockeyDescription": "+1 nopeus"},
    {"horseName": "Tuulikki", "jockeyName": "Pelkuri", "jockeyDescription": "Ei osallistu tappeluksiin"},
    {"horseName": "Laukki",   "jockeyName": "Raju",    "jockeyDescription": "Boost vie tuplasti eteenpäin"},
]

TEST_RACE_ROUND_RAVIT = RaceRoundEvent(
    roundNumber=3,
    trackLength=20,
    positions=[
        {"id": 1, "name": "Ukko",     "position": 12, "status": "racing",
         "tiredRoundsLeft": 0, "stumbleRoundsLeft": 0, "motivatedRoundsLeft": 0, "fightRoundsLeft": 0, "confusedRoundsLeft": 0},
        {"id": 2, "name": "Tuulikki", "position": 8,  "status": "racing",
         "tiredRoundsLeft": 1, "stumbleRoundsLeft": 0, "motivatedRoundsLeft": 0, "fightRoundsLeft": 0, "confusedRoundsLeft": 0},
        {"id": 3, "name": "Laukki",   "position": 5,  "status": "dead",
         "tiredRoundsLeft": 0, "stumbleRoundsLeft": 0, "motivatedRoundsLeft": 0, "fightRoundsLeft": 0, "confusedRoundsLeft": 0},
    ],
    raceEvents=[
        {"horseName": "Laukki", "eventType": "death", "detail": "Laukki kaatuu ja poistuu kilpailusta!"},
    ],
)

TEST_RAVIT_FINAL_POSITIONS = [
    {"horseId": 1, "horseName": "Ukko",     "position": 20, "place": 1, "status": "racing"},
    {"horseId": 2, "horseName": "Tuulikki", "position": 14, "place": 2, "status": "racing"},
    {"horseId": 3, "horseName": "Laukki",   "position": 5,  "place": 4, "status": "dead"},
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

TEST_BETTOR_DRINK_RAVIT = RavitBettorDrinkEvent(
    playerName="Testi Matti",
    horseName="Laukki",
    amount=2,
    reason="hevonen kuoli taistelussa",
    scores=[
        {"name": "Testi Tatti", "drank": 0},
        {"name": "Testi Matti", "drank": 2},
    ],
)

# ---------------------------------------------------------------------------
# Mexico
# ---------------------------------------------------------------------------

TEST_MEXICO_CHALLENGE = MexicanChallengeEvent(
    challenger="Testi Matti",
    claimer="Testi Tatti",
    claimed=65,
    actual=43,
    d1=4,
    d2=3,
    loser="Testi Tatti",
    drinks=1,
    wasMexico=False,
)

TEST_MEXICO_CHALLENGE_MEXICO = MexicanChallengeEvent(
    challenger="Testi Matti",
    claimer="Testi Tatti",
    claimed=1000,
    actual=43,
    d1=4,
    d2=3,
    loser="Testi Tatti",
    drinks=2,
    wasMexico=True,
)

TEST_MEXICO_SCORES = [
    {"name": "Testi Tatti", "drank": 3, "gave": 0},
    {"name": "Testi Matti", "drank": 1, "gave": 0},
]

# ---------------------------------------------------------------------------
# Game → parts registry  (used by cli.py to build the two-level menu)
# ---------------------------------------------------------------------------

GAMES = {
    "Mexico": [
        ("mexico-challenge", "Haaste"),
        ("mexico-tally", "Loppusaldo"),
    ],
    "Buja": [
        ("turns", "Vuorokuitit"),
        ("hands", "Kädet"),
        ("board", "Lautakortit"),
        ("tally", "Loppulasku"),
    ],
    "TaskGame": [
        ("tasks", "Tehtäväkortit"),
    ],
    "Ravit": [
        ("ravit-betting",      "Hevoset & Vedonlyönti"),
        ("ravit-rata",         "Kierros"),
        ("ravit-event",        "Tapahtuma"),
        ("ravit-bettor-drink", "Veikkaajan juomat"),
        ("ravit-tiebreak",     "Tasapeli"),
        ("ravit-winner",       "Voittaja"),
        ("ravit-final",        "Lopputulos"),
    ],
}


def printTestReceipts(printer, parts=None) -> None:
    """Print test receipts. Pass None to print every part of every game."""
    if parts is None:
        parts = [key for game_parts in GAMES.values() for key, _ in game_parts]

    if "mexico-challenge" in parts:
        printer.printWith(lambda p, e=TEST_MEXICO_CHALLENGE: formatMexicoChallenge(e, p))
        printer.printWith(lambda p, e=TEST_MEXICO_CHALLENGE_MEXICO: formatMexicoChallenge(e, p))

    if "mexico-tally" in parts:
        printer.printWith(lambda p: formatMexicoTally(TEST_MEXICO_SCORES, p))

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
        printer.printWith(lambda p: formatHorseList(TEST_HORSES_RAVIT, p))
        printer.printWith(lambda p: formatJockeyList(TEST_JOCKEYS_RAVIT, p))
        printer.printWith(lambda p: formatBettingReceipt(TEST_HORSES_RAVIT, TEST_BETS_RAVIT, p))

    if "ravit-rata" in parts:
        if TEST_RACE_ROUND_RAVIT.raceEvents:
            printer.printWith(lambda p, e=TEST_RACE_ROUND_RAVIT: formatRaceEvents(e, p))
        printer.printWith(lambda p, e=TEST_RACE_ROUND_RAVIT: formatRaceTrack(e, p))

    if "ravit-event" in parts:
        printer.printWith(lambda p, e=TEST_HORSE_EVENT_RAVIT: formatHorseEvent(e, p))

    if "ravit-bettor-drink" in parts:
        printer.printWith(lambda p, e=TEST_BETTOR_DRINK_RAVIT: formatBettorDrink(e, p))

    if "ravit-winner" in parts:
        winner = TEST_RAVIT_FINAL_POSITIONS[0]
        winnerData = {
            "horseName": winner["horseName"],
            "odds": next(h["odds"] for h in TEST_HORSES_RAVIT if h["id"] == winner["horseId"]),
            "bettors": [{"player": b["player"], "amount": b["amount"]} for b in TEST_BETS_RAVIT if b["horseId"] == winner["horseId"]],
        }
        printer.printWith(lambda p, d=winnerData: formatRavitWinner(d, p))

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
