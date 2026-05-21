"""
Randomised penalties for the loser of a competition (e.g. Kuolema, ravit).
Import drawPenalty() in any game that needs to assign a random punishment.

Each penalty has:
    title       -- short name shown in bold on the receipt
    description -- what the loser must do
    drinks      -- fixed drink count (int), or None if social/no tracking
    drinkType   -- "take"   loser drinks the amount
                   "give"   loser gives out the amount
                   "social" no automatic tracking; resolve at the table
    duration    -- number of turns the effect lasts (int), or None if one-shot
                   duration is counted in card draws (turns), not rounds
"""
import random

PENALTIES = [
    {
        "title": "Bonus juomat",
        "description": "Juo 5 juomaa rangaistuksena.",
        "drinks": 5,
        "drinkType": "take",
        "duration": None,
    },
    {
        "title": "Iso rangaistus",
        "description": "Juo 8 juomaa rangaistuksena.",
        "drinks": 8,
        "drinkType": "take",
        "duration": None,
    },
    {
        "title": "Kaksinkertainen",
        "description": "Seuraavat 3 juomaasi ovat kaksinkertaisia.",
        "drinks": None,
        "drinkType": "social",
        "duration": 3,
    },
    {
        "title": "Buffalo",
        "description": "Juo seuraavat 2 juomaa vasemmalla kädellä.",
        "drinks": None,
        "drinkType": "social",
        "duration": 2,
    },
    {
        "title": "Mykkä",
        "description": "Et saa puhua kahteen vuoroon ennen kuin seuraava kortti on nostettu. Puhuminen = 3 juomaa.",
        "drinks": None,
        "drinkType": "social",
        "duration": 2,
    },
    {
        "title": "Puoliaika",
        "description": "Juo 4 juomaa ja valitse yksi pelaaja joka juo 2.",
        "drinks": None,
        "drinkType": "social",
        "duration": None,
    },
    {
        "title": "Puhuttelu",
        "description": "Aloitat puheesi aina sanoilla 'Arvon juomakansa' seuraavan 3 kortin ajan",
        "drinks": None,
        "drinkType": "social",
        "duration": 3,
    },
    {
        "title": "Puhuttelu",
        "description": "Aloitat puheesi aina sanoilla 'Arvon kanssajuojat minulla on asiaa' seuraavan 3 kortin ajan",
        "drinks": None,
        "drinkType": "social",
        "duration": 3,
    },
]


def drawPenalty() -> dict:
    """Return a random penalty from the list."""
    return random.choice(PENALTIES)
