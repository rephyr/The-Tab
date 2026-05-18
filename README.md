# kuittipeli

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
