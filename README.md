# The-Tab

A CLI card drinking game that uses a receipt printer to play.

## Requirements

Python 3.10 or newer. For thermal printer support, install python-escpos:

```
pip install python-escpos
```

## Running

```
python main.py
```

Or with make:

```
make run
```
for editing data run 
```
make run-admin
```
or
```
python main.py admin
```

## Testing

```
make test
```

## Configuration

Edit `config.json` to set up the printer and adjust game settings.

**Printer options** (`connection` field):

* `stdout` prints to terminal
* `win32raw` Windows thermal printer, set `printerName`

**Buja settings:**

* `boardLength` number of rows in the board phase
* `boardStartDrinks` drinks on the first board row
* `boardIncrement` drinks added per row
* `drinkAmount` drinks for a wrong guess in the phase rounds
* `deckCount` number of decks to use

## Games

### Buja

A card guessing game. Players go through four phases:

1. Red or Black
2. Higher or Lower
3. Inside or Outside
4. Suit

Then everyone plays a shared board phase where cards are revealed one by one. Each card has an action (drink, give, or share). Players who have a matching rank in hand must perform the action. The final card is always share and worth double the last row.

Settings for this game can be adjusted before each game from the CLI without editung the config file.

### TaskGame

A turn-based task card game. Players take turns drawing a random task from a shuffled deck. Each task tells a player what to do. Drink, give drinks, start a social challenge, or create a persistent link between players. The game ends when the deck runs.

**Task types:**

* `take` — drawer takes a fixed number of drinks
* `give` — drawer gives drinks to a chosen player
* `social` — open-ended challenge; game master logs drinks manually as `Name:N` pairs
* `link` — creates a persistent link (Pari, Huora); linked players share drinks automatically
* `special` — ongoing effect with no immediate drinks (Sääntö, Kysymysmestari, Immunitetti, Tupla)
* `roulette` — sequential pulls with one guaranteed hit; hit player drinks

**During the game:**

* Press `d` at the draw prompt to see how many cards remain (`Cards left: X/Y`).
* Press `q` after any card to quit early and print the tally.

**TaskGame settings** (`config.json`):

* `commonCount` — how many copies of common cards go in the deck (default: 4)
* `specialCount` — how many copies of special/rare cards go in the deck (default: 2)

Settings can be adjusted before each game from the CLI without editing the config file.
